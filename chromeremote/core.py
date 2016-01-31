'''
chromeremote.core
=================
Core functionality
'''
import asyncio
import chromeremote.ui as ui


def main(loop=None):
    ''' Runs the main UI loop. Blocks until the program exits. '''
    if loop is None:
        loop = asyncio.get_event_loop()

    ui_task = ui.create_task(loop)
    try:
        loop.run_until_complete(ui_task)
    finally:
        loop.close()


if __name__ == "__main__":
    main()
