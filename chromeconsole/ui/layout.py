'''
chromeconsole.ui.layout
======================
UI Layouts
'''
from prompt_toolkit.filters import Condition
from prompt_toolkit.layout.containers import (
    HSplit, Window, ConditionalContainer, FloatContainer, Float)
from prompt_toolkit.layout.controls import BufferControl, FillControl
from prompt_toolkit.layout.dimension import LayoutDimension as D
from prompt_toolkit.layout.processors import BeforeInput
from pygments.token import Token

from .const import DEFAULT_BUFFER, COMMAND_BUFFER, TAB_SELECT_BUFFER


class CommandPrompt(Window):
    ''' Command prompt displayed at the bottom of the screen. '''
    PROMPT = '> '

    def __init__(self):
        super(CommandPrompt, self).__init__(
            BufferControl(
                buffer_name=COMMAND_BUFFER,
                input_processors=[BeforeInput.static(self.PROMPT)],
            ),
            height=D.exact(1)
        )


class TabSelectWindow(Window):
    ''' Tab selection window used when connecting. '''
    def __init__(self):
        super(TabSelectWindow, self).__init__(
            BufferControl(buffer_name=TAB_SELECT_BUFFER),
        )


class MainWindow(Window):
    ''' Main window displayed after connecting. '''
    def __init__(self):
        super(MainWindow, self).__init__(
            BufferControl(buffer_name=DEFAULT_BUFFER),
        )


class Layout(object):
    ''' Contains the layout for an application. '''
    # pylint: disable=too-few-public-methods
    def __init__(self, app):
        self.app = app
        self.layout = FloatContainer(
            content=HSplit([
                # main window
                MainWindow(),

                # horizontal split
                Window(height=D.exact(1),
                       content=FillControl('\u2500', token=Token.Line)),

                # command prompt
                CommandPrompt(),
            ]),
            floats=[
                Float(left=0, right=0, top=0, bottom=2, content=HSplit([
                    ConditionalContainer(
                        content=TabSelectWindow(),
                        filter=Condition(self.is_connecting),
                    ),
                ])),
            ]
        )

    def is_connecting(self, cli):
        ''' Returns True if the app is currently connecting to an instance. '''
        # pylint: disable=unused-argument
        return self.app.is_connecting
