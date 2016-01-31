'''
chromeremote.ui
===============
UI Implementation
'''
import asyncio

from prompt_toolkit.application import Application, AbortAction
from prompt_toolkit.buffer import Buffer
from prompt_toolkit.interface import CommandLineInterface
from prompt_toolkit.shortcuts import create_asyncio_eventloop

from .layout import Layout
from .const import DEFAULT_BUFFER, COMMAND_BUFFER
from .keybindings import Keybindings


class ChromeRemoteApplication(object):
    ''' Main application object. '''
    # pylint: disable=too-few-public-methods
    def __init__(self):
        self.layout = Layout()
        self.bindings = Keybindings()
        self.buffers = {
            DEFAULT_BUFFER: Buffer(is_multiline=True),
            COMMAND_BUFFER: Buffer(),
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

    @asyncio.coroutine
    def run_async(self):
        ''' Runs the user interface as an async task. '''
        eventloop = create_asyncio_eventloop()
        self.cli = CommandLineInterface(application=self.application,
                                        eventloop=eventloop)
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
        app = ChromeRemoteApplication()
    return loop.create_task(app.run_async())
