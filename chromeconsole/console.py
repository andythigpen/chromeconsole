'''
chromeconsole.console
=================
Console operations
See https://developer.chrome.com/devtools/docs/protocol/1.1/console
'''


class ChromeConsole(object):
    ''' Commands for the Console domain mode. '''
    def __init__(self, websocket):
        self.websocket = websocket

    def enable(self, callback=None):
        ''' Enables the Chrome console domain. Returns a Future. '''
        return self.websocket.call_method('Console.enable', callback=callback)

    def disable(self, callback=None):
        ''' Disables the Chrome console domain. Returns a Future. '''
        return self.websocket.call_method('Console.disable', callback=callback)
