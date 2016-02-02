'''
chromeconsole.ui
===============
UI Implementation
'''
import asyncio
import requests

from prompt_toolkit.application import Application, AbortAction
from prompt_toolkit.buffer import Buffer, AcceptAction
from prompt_toolkit.interface import CommandLineInterface
from prompt_toolkit.shortcuts import create_asyncio_eventloop
from prompt_toolkit.styles import DynamicStyle

from .layout import Layout
from .const import DEFAULT_BUFFER, COMMAND_BUFFER
from .keybindings import Keybindings
from .commands import handle_command
from .style import get_style


class ChromeConsoleApplication(object):
    ''' Main application object. '''
    def __init__(self, loop):
        self.is_selecting_tab = False
        self.loop = loop
        layout = Layout(self)
        bindings = Keybindings()
        buffers = {
            DEFAULT_BUFFER: Buffer(is_multiline=True),
            COMMAND_BUFFER: Buffer(
                accept_action=AcceptAction(handler=self.handle_action),
            ),
        }
        self.application = Application(
            layout=layout.layout,
            buffers=buffers,
            style=DynamicStyle(lambda: get_style('default')),
            key_bindings_registry=bindings.registry,
            use_alternate_screen=True,
            on_abort=AbortAction.RAISE_EXCEPTION,
            on_exit=AbortAction.RAISE_EXCEPTION,
        )
        self.cli = None
        self.tabs = []

    def handle_action(self, cli, buffer):
        ''' Executes commands received from command prompt. '''
        # pylint: disable=unused-argument
        handle_command(self, buffer.text)
        # clears the buffer
        buffer.reset()

    def _display_tab_list(self, future):
        ''' Callback that outputs list of tabs to default buffer. '''
        response = future.result()
        self.tabs = response.json()
        self.is_selecting_tab = True
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
        app = ChromeConsoleApplication(loop)
    return loop.create_task(app.run_async())
