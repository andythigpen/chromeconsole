'''
chromeconsole.ui.commands
========================
'''
import re


class Command(object):
    ''' Decorator that caches all commands. '''
    # pylint: disable=too-few-public-methods
    commands = []

    def __init__(self, regex):
        self.regex = re.compile(regex)

    def __call__(self, func):
        self.commands.append((self.regex, func))
        return func

    @classmethod
    def exec(cls, app, text):
        ''' Finds a matching command and executes it. '''
        for regex, func in cls.commands:
            match = regex.match(text)
            if match:
                func(match, app)
                return


@Command('^q(uit)?$')
def quit_app(match, app):
    ''' Exits the application. '''
    # pylint: disable=unused-argument
    app.cli.set_return_value(None)


@Command('^c(onnect)? ?(?P<host>.*)?(:(?P<port>[0-9]+))?$')
def connect(match, app):
    ''' Exits the application. '''
    host = match.group('host') or 'localhost'
    port = match.group('port') or 9222
    app.load_tab_list(host, port)


def handle_command(app, text):
    ''' Convenience function for Command.exec. '''
    Command.exec(app, text)
