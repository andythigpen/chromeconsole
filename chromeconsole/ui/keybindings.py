'''
chromeconsole.ui.keybindings
===========================
UI key bindings
'''
from prompt_toolkit.filters import Condition
from prompt_toolkit.key_binding.manager import KeyBindingManager
from prompt_toolkit.key_binding.bindings.utils import create_handle_decorator
from prompt_toolkit.key_binding.bindings.vi import ViStateFilter
from prompt_toolkit.key_binding.vi_state import InputMode
from prompt_toolkit.keys import Keys


def create_key_bindings(app):
    ''' Contains the key bindings for an application. '''
    # pylint: disable=unused-argument,unused-variable
    manager = KeyBindingManager(
        enable_abort_and_exit_bindings=True,
        enable_vi_mode=True,
    )

    in_insert_mode = ViStateFilter(manager.get_vi_state, InputMode.INSERT)
    is_selecting_tab = Condition(lambda cli: app.is_selecting_tab)

    handle = create_handle_decorator(manager.registry)

    @handle('j', filter=is_selecting_tab & in_insert_mode)
    def select_down(event):
        ''' Selects the next tab down in the list. '''
        app.select_tab_down()

    @handle('k', filter=is_selecting_tab & in_insert_mode)
    def select_up(event):
        ''' Selects the next tab up in the list. '''
        app.select_tab_up()

    @handle(Keys.ControlF, filter=is_selecting_tab & in_insert_mode)
    def select_page_down(event):
        ''' Page down in tab list. '''
        tab_select = app.get_window('tab-select')
        height = tab_select.render_info.window_height
        app.select_tab_down(height)

    @handle(Keys.ControlB, filter=is_selecting_tab & in_insert_mode)
    def select_page_up(event):
        ''' Page down in tab list. '''
        tab_select = app.get_window('tab-select')
        height = tab_select.render_info.window_height
        app.select_tab_up(height)

    @handle('g', 'g', filter=is_selecting_tab & in_insert_mode)
    def select_bottom(event):
        ''' Bottom of tab list. '''
        tab_select = app.get_window('tab-select')
        height = tab_select.render_info.content_height
        app.select_tab_down(height)

    @handle('G', filter=is_selecting_tab & in_insert_mode)
    def select_top(event):
        ''' Top of tab list. '''
        app.selected_tab = 0

    return manager
