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


class ChromeWebSocket(object):
    ''' Manages a websocket for communicating with Chrome. '''
    def __init__(self, url, loop=None):
        self.url = url
        if loop is None:
            loop = asyncio.get_event_loop()
        self.loop = loop
        self.websock = None
        self._message_id = 0
        self._message_id_lock = threading.Lock()
        self._futures = {}

    def _get_message_id(self):
        ''' Returns a unique id for a JSON message. '''
        with self._message_id_lock:
            self._message_id += 1
            return self._message_id

    def _schedule(self, coroutine):
        ''' Schedules a coroutine on the event loop. '''
        # pylint: disable=deprecated-method
        asyncio.async(coroutine, loop=self.loop)

    def connect(self):
        '''
        Connects to a websocket at the given URL.
        Returns a future.
        '''
        future = asyncio.Future()

        @asyncio.coroutine
        def connect_ws():
            ''' Connect coroutine. '''
            self.websock = yield from websockets.connect(self.url)
            future.set_result(True)

        self._schedule(connect_ws())
        return future

    def start_loop(self, handler):
        '''
        Reads messages from websocket and passes them to handler in a loop.
        The connect method must be called before this.
        handler should be a coroutine.
        '''
        @asyncio.coroutine
        def loop_ws():
            ''' Continous loop that handles messages. '''
            while True:
                data = yield from self.websock.recv()
                response = json.loads(data)
                response_id = response.get('id', None)
                if response_id in self._futures:
                    future = self._futures[response_id]
                    future.set_result(response)
                else:
                    yield from handler(response)

        self._schedule(loop_ws())

    def call_method(self, method, params=None, callback=None):
        '''
        Calls a remote method via the websocket with an optional param dict.
        If callback is specified, the returned future will be set when the
        response is received.  Otherwise, it will be set when the message
        has been sent.
        '''
        future = asyncio.Future()

        @asyncio.coroutine
        def call_method_ws():
            ''' Actually sends the data via the websocket. '''
            data = {
                'id': self._get_message_id(),
                'method': method,
            }
            if params is not None:
                data['params'] = params
            if callback is not None:
                future.add_done_callback(callback)
                self._futures[data['id']] = future
            yield from self.websock.send(json.dumps(data))
            if callback is not None:
                future.set_result(True)

        # pylint: disable=deprecated-method
        self._schedule(call_method_ws())
        return future


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
