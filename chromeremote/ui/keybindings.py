from prompt_toolkit.key_binding.manager import KeyBindingManager

manager = KeyBindingManager(
    enable_abort_and_exit_bindings=True,
    enable_vi_mode=True,
)
