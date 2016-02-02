'''
chromeconsole.ui.layout
======================
UI Layouts
'''
from prompt_toolkit.filters import Condition
from prompt_toolkit.layout.containers import (
    HSplit, Window, ConditionalContainer, FloatContainer, Float)
from prompt_toolkit.layout.controls import (
    BufferControl, FillControl, TokenListControl)
from prompt_toolkit.layout.dimension import LayoutDimension as D
from prompt_toolkit.layout.processors import BeforeInput
from prompt_toolkit.layout.screen import Char
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
            height=D.exact(1)
        )


class TabSelectWindow(Window):
    ''' Tab selection window used when connecting. '''
    def __init__(self, app):
        self.app = app
        self.token = Token.TabSelectWindow
        self.current = 0
        self.selected = 0
        super(TabSelectWindow, self).__init__(
            TokenListControl(get_tokens=self.get_tokens,
                             get_default_char=self.get_default_char),
        )

    def get_tokens(self, cli):
        ''' Returns a list of tokens used to display the tab list. '''
        # pylint: disable=unused-argument
        tabs = self.app.tabs
        tokens = []
        for idx, tab in enumerate(tabs):
            if idx == self.selected:
                tokens.extend([
                    (self.token.Selected, '{:2d})'.format(idx)),
                    (self.token.Selected, '  {}\n'.format(tab['title'])),
                ])
            else:
                tokens.extend([
                    (self.token.Number, '{:2d})'.format(idx)),
                    (self.token.Text, '  {}\n'.format(tab['title'])),
                ])
        return tokens

    def get_default_char(self, cli):
        ''' Returns the default background character for a line. '''
        # pylint: disable=unused-argument
        return Char(' ', self.token)


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
                        content=TabSelectWindow(app),
                        filter=Condition(self.is_selecting_tab),
                    ),
                ])),
            ]
        )

    def is_selecting_tab(self, cli):
        ''' Returns True if the app is currently selecting a tab. '''
        # pylint: disable=unused-argument
        return self.app.is_selecting_tab
