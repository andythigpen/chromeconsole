'''
chromeremote.ui
===============
UI Implementation
'''
import asyncio
import requests

from prompt_toolkit.application import Application, AbortAction
from prompt_toolkit.buffer import Buffer, AcceptAction
from prompt_toolkit.interface import CommandLineInterface
from prompt_toolkit.shortcuts import create_asyncio_eventloop

from .layout import Layout
from .const import DEFAULT_BUFFER, COMMAND_BUFFER, TAB_SELECT_BUFFER
from .keybindings import Keybindings
from .commands import handle_command


class ChromeRemoteApplication(object):
    ''' Main application object. '''
    def __init__(self, loop):
        self.is_connecting = False
        self.loop = loop
        self.layout = Layout(self)
        self.bindings = Keybindings()
        self.buffers = {
            DEFAULT_BUFFER: Buffer(is_multiline=True),
            COMMAND_BUFFER: Buffer(
                accept_action=AcceptAction(handler=self.handle_action),
            ),
            TAB_SELECT_BUFFER: Buffer(is_multiline=True),
        }
        self.application = Application(
            layout=self.layout.layout,
            buffers=self.buffers,
            key_bindings_registry=self.bindings.registry,
            use_alternate_screen=True,
            on_abort=AbortAction.RAISE_EXCEPTION,
            on_exit=AbortAction.RAISE_EXCEPTION,
        )
        self.cli = None

    def handle_action(self, cli, buffer):
        ''' Executes commands received from command prompt. '''
        # pylint: disable=unused-argument
        handle_command(self, buffer.text)
        # clears the buffer
        buffer.reset()

    def _display_tab_list(self, future):
        ''' Callback that outputs list of tabs to default buffer. '''
        response = future.result()
        tabs = response.json()
        text = ''
        self.is_connecting = True
        for idx, tab in enumerate(tabs):
            text += '{:02d}:  {}\n'.format(idx, tab['title'])
        self.buffers[TAB_SELECT_BUFFER].text = text
        self.cli.focus(TAB_SELECT_BUFFER)
        self.cli.invalidate()

    def load_tab_list(self, host='127.0.0.1', port=9222):
        '''
        Loads the list of Chrome tabs from the given host.
        Chrome remote debugging must have been enabled using the
        --remote-debugging-port command line option.
        '''
        url = 'http://{}:{}/json'.format(host, port)
        future = self.loop.run_in_executor(None, requests.get, url)
        future.add_done_callback(self._display_tab_list)
        # pylint: disable=deprecated-method
        asyncio.async(future)

    @asyncio.coroutine
    def run_async(self):
        ''' Runs the user interface as an async task. '''
        eventloop = create_asyncio_eventloop()
        self.cli = CommandLineInterface(application=self.application,
                                        eventloop=eventloop)
        self.cli.focus(COMMAND_BUFFER)
        try:
            while True:
                result = yield from self.cli.run_async()
                if result is None:
                    print('Exiting...')
                    return
        except (EOFError, KeyboardInterrupt):
            return
        finally:
            eventloop.close()


@asyncio.coroutine
def create_task(loop, app=None):
    '''
    Returns an asyncio task, optionally creating a default app if not provided.
    '''
    if app is None:
        app = ChromeRemoteApplication(loop)
    return loop.create_task(app.run_async())
