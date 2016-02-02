'''
chromeconsole.ui.style
======================
UI styles
'''
from prompt_toolkit.styles import PygmentsStyle
from pygments.styles import get_style_by_name
from pygments.token import Token

STYLE_EXTENSIONS = {
    Token.TabSelectWindow.Number: '#00ffff',
    Token.TabSelectWindow.Selected: '#000000 bg:#00ffff',
}


def get_style(name):
    ''' Returns a Style object given a name. '''
    style_cls = get_style_by_name(name)
    styles = {}
    styles.update(STYLE_EXTENSIONS)
    return PygmentsStyle.from_defaults(styles, pygments_style_cls=style_cls)
