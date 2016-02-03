'''
chromeconsole.console
=================
Console operations
See https://developer.chrome.com/devtools/docs/protocol/1.1/console
'''
import asyncio
import json
from .core import get_message_id


@asyncio.coroutine
def enable_console(websock):
    ''' Enables the Chrome console domain. '''
    yield from websock.send(json.dumps({
        'id': get_message_id(),
        'method': 'Console.enable',
    }))


@asyncio.coroutine
def disable_console(websock):
    ''' Disnables the Chrome console domain. '''
    yield from websock.send(json.dumps({
        'id': get_message_id(),
        'method': 'Console.disable',
    }))
