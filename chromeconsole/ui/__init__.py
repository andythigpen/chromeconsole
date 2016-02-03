'''
chromeconsole.ui
===============
UI Implementation
'''
import asyncio

from prompt_toolkit.application import Application, AbortAction
from prompt_toolkit.buffer import Buffer, AcceptAction
from prompt_toolkit.interface import CommandLineInterface
from prompt_toolkit.shortcuts import create_asyncio_eventloop
from prompt_toolkit.styles import DynamicStyle

from .layout import Layout
from .const import DEFAULT_BUFFER, COMMAND_BUFFER
from .keybindings import create_key_bindings
from .commands import handle_command
from .style import get_style
from ..core import load_tab_list, connect_ws, loop_ws
from ..console import enable_console


class ChromeConsoleApplication(object):
    ''' Main application object. '''
    # pylint: disable=too-many-instance-attributes
    def __init__(self, loop):
        self.loop = loop
        self.layout = Layout(self)
        bindings = create_key_bindings(self)
        self.buffers = {
            DEFAULT_BUFFER: Buffer(is_multiline=True),
            COMMAND_BUFFER: Buffer(
                accept_action=AcceptAction(handler=self.handle_action),
            ),
        }
        self.application = Application(
            layout=self.layout.layout,
            buffers=self.buffers,
            style=DynamicStyle(lambda: get_style('default')),
            key_bindings_registry=bindings.registry,
            use_alternate_screen=True,
            on_abort=AbortAction.RAISE_EXCEPTION,
            on_exit=AbortAction.RAISE_EXCEPTION,
        )
        self.cli = None
        self.tabs = []
        self.is_selecting_tab = False
        self.selected_tab = 0
        self.websock = None

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
        ''' Loads the list of Chrome tabs from the given host. '''
        future = load_tab_list(host, port, loop=self.loop)
        future.add_done_callback(self._display_tab_list)

    def select_tab(self):
        ''' Selects the currently highlighted tab. '''
        tab = self.tabs[self.selected_tab]
        url = tab['webSocketDebuggerUrl']
        future = connect_ws(url)
        future.add_done_callback(self._connected)
        self.tabs = []
        self.is_selecting_tab = False
        self.selected_tab = 0
        self.buffers[DEFAULT_BUFFER].text = 'Connecting to {}...\n'.format(url)

    def move_tab_choice_down(self, lines=1):
        ''' Selects a tab down in the tab select list. '''
        self.selected_tab = min(self.selected_tab + lines, len(self.tabs) - 1)

    def move_tab_choice_up(self, lines=1):
        ''' Selects a tab up in the tab select list. '''
        self.selected_tab = max(self.selected_tab - lines, 0)

    def get_window(self, name):
        ''' Returns a window by name. '''
        return self.layout.windows[name]

    def _connected(self, future):
        ''' Callback once the websocket has connected. '''
        self.websock = future.result()
        # pylint: disable=deprecated-method
        asyncio.async(loop_ws(self.websock, self.handle_message))
        self.buffers[DEFAULT_BUFFER].text += 'Connected.\n'
        self.cli.invalidate()
        asyncio.async(enable_console(self.websock))

    @asyncio.coroutine
    def handle_message(self, msg):
        ''' Handles a message from the websocket. '''
        self.buffers[DEFAULT_BUFFER].text += '{}\n'.format(msg)
        self.cli.invalidate()

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
