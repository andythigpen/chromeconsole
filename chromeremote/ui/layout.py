'''
chromeremote.ui.layout
======================
UI Layouts
'''
from prompt_toolkit.layout.containers import HSplit, Window
from prompt_toolkit.layout.controls import BufferControl, FillControl
from prompt_toolkit.layout.dimension import LayoutDimension as D
from prompt_toolkit.layout.processors import BeforeInput
from pygments.token import Token

from .const import DEFAULT_BUFFER, COMMAND_BUFFER


class CommandPrompt(Window):
    ''' Command prompt displayed at the bottom of the screen. '''
    PROMPT = '> '

    def __init__(self):
        super(CommandPrompt, self).__init__(
            BufferControl(
                buffer_name=COMMAND_BUFFER,
                input_processors=[BeforeInput.static(self.PROMPT)],
            ),
            height=D.exact(1))


class Layout(object):
    ''' Contains the layout for an application. '''
    # pylint: disable=too-few-public-methods
    def __init__(self):
        self.layout = HSplit([
            # main window
            Window(content=BufferControl(buffer_name=DEFAULT_BUFFER)),

            # horizontal split
            Window(height=D.exact(1),
                   content=FillControl('\u2500', token=Token.Line)),

            # command prompt
            CommandPrompt(),
        ])
