from prompt_toolkit.application import Application, AbortAction
from prompt_toolkit.buffer import Buffer
from prompt_toolkit.interface import CommandLineInterface
from prompt_toolkit.shortcuts import create_asyncio_eventloop
import asyncio

from .layout import layout
from .const import DEFAULT_BUFFER
from .keybindings import manager

buffers={
    DEFAULT_BUFFER: Buffer(is_multiline=True),
}

application = Application(
    layout=layout,
    buffers=buffers,
    key_bindings_registry=manager.registry,
    use_alternate_screen=True,
    on_abort=AbortAction.RAISE_EXCEPTION,
    on_exit=AbortAction.RAISE_EXCEPTION,
)


@asyncio.coroutine
def run_async():
    ''' Runs the user interface as an async task. '''
    eventloop = create_asyncio_eventloop()
    cli = CommandLineInterface(application=application, eventloop=eventloop)
    try:
        while True:
            result = yield from cli.run_async()
            if result is None:
                print('Exiting...')
                return
    except (EOFError, KeyboardInterrupt):
        return
    finally:
        eventloop.close()
