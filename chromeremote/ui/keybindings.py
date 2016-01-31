'''
chromeremote.ui.keybindings
===========================
UI key bindings
'''
from prompt_toolkit.key_binding.manager import KeyBindingManager


class Keybindings(object):
    ''' Contains the key bindings for an application. '''
    # pylint: disable=too-few-public-methods
    def __init__(self):
        self.manager = KeyBindingManager(
            enable_abort_and_exit_bindings=True,
            enable_vi_mode=True,
        )

    @property
    def registry(self):
        ''' Shortcut that returns KeyBindingManager's registry. '''
        return self.manager.registry
