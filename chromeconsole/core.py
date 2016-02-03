'''
chromeconsole.core
=================
Core functionality
'''
import asyncio
import json
import threading
import requests
import websockets


_id = 0
_id_lock = threading.Lock()


def get_message_id():
    ''' Returns a unique id for a JSON message. '''
    global _id
    with _id_lock:
        _id += 1
        return _id


def load_tab_list(host='127.0.0.1', port=9222, loop=None):
    '''
    Loads the list of Chrome tabs from the given host.
    Chrome remote debugging must have been enabled using the
    --remote-debugging-port command line option.
    Returns a future.
    '''
    if loop is None:
        loop = asyncio.get_event_loop()
    url = 'http://{}:{}/json'.format(host, port)
    future = loop.run_in_executor(None, requests.get, url)
    # pylint: disable=deprecated-method
    asyncio.async(future)
    return future


def connect_ws(url):
    '''
    Connects to a websocket at the given URL.
    Returns a future.
    '''
    future = asyncio.Future()

    @asyncio.coroutine
    def connect():
        ''' Connect coroutine. '''
        websock = yield from websockets.connect(url)
        future.set_result(websock)

    # pylint: disable=deprecated-method
    asyncio.async(connect())
    return future


@asyncio.coroutine
def loop_ws(websock, handler):
    '''
    Reads messages from websock and passes them to a handler continuously.
    websock should already be connected.
    handler should be a coroutine.
    '''
    while True:
        message = yield from websock.recv()
        yield from handler(json.loads(message))


def main(loop=None):
    ''' Runs the main UI loop. Blocks until the program exits. '''
    import chromeconsole.ui as ui

    if loop is None:
        loop = asyncio.get_event_loop()

    app = ui.ChromeConsoleApplication(loop)
    ui_task = ui.create_task(loop, app)
    try:
        loop.run_until_complete(ui_task)
    finally:
        loop.close()
