'''
chromeremote.ui.layout
======================
UI Layouts
'''
from functools import partial
from prompt_toolkit.filters import Condition
from prompt_toolkit.layout.containers import (
    HSplit, Window, ConditionalContainer)
from prompt_toolkit.layout.controls import BufferControl, FillControl
from prompt_toolkit.layout.dimension import LayoutDimension as D
from prompt_toolkit.layout.processors import BeforeInput
from pygments.token import Token

from .const import DEFAULT_BUFFER, COMMAND_BUFFER, TAB_SELECT_BUFFER


def is_connecting(app, cli):
    ''' Returns True if the app is currently connecting to an instance. '''
    # pylint: disable=unused-argument
    return app.is_connecting


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


class TabSelectWindow(ConditionalContainer):
    ''' Tab selection window used when connecting. '''
    def __init__(self, app):
        super(TabSelectWindow, self).__init__(
            Window(BufferControl(buffer_name=TAB_SELECT_BUFFER)),
            filter=Condition(partial(is_connecting, app)),
        )


class MainWindow(ConditionalContainer):
    ''' Main window displayed after connecting. '''
    def __init__(self, app):
        super(MainWindow, self).__init__(
            Window(BufferControl(buffer_name=DEFAULT_BUFFER)),
            filter=~Condition(partial(is_connecting, app)),
        )


class Layout(object):
    ''' Contains the layout for an application. '''
    # pylint: disable=too-few-public-methods
    def __init__(self, app):
        self.layout = HSplit([
            # main window
            MainWindow(app),
            TabSelectWindow(app),

            # horizontal split
            Window(height=D.exact(1),
                   content=FillControl('\u2500', token=Token.Line)),

            # command prompt
            CommandPrompt(),
        ])
