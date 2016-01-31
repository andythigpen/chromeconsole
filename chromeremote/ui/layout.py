from prompt_toolkit.layout.containers import VSplit, HSplit, Window
from prompt_toolkit.layout.controls import BufferControl
from .const import DEFAULT_BUFFER

layout = VSplit([
    Window(content=BufferControl(buffer_name=DEFAULT_BUFFER)),
])
