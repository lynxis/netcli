#!/usr/bin/env python3

from jsonubus import JsonUbus
import readline
import logging
import sys
import argparse

LOG = logging.getLogger('netcli')

def convert_to_dict(argumentlist):
    """ convert a list into a dict
        e.g. ['help=me', 'foo'='bar'] => {'help': 'me', 'foo':'bar'}
    """
    def gen_dict(keyval):
        pos = keyval.find('=')
        if pos == -1:
            raise RuntimeError("Invalid argument {}".format(keyval))
        return {keyval[:pos]:keyval[pos+1:]}
    converted = {}
    for i in [gen_dict(part) for part in argumentlist]:
        converted.update(i)
    return converted

class CliApp(object):
    def __init__(self):
        self.__prompt = "netcli#>"
        self.__command = {}
        self.__commands = []
        self.__completer = []
        self.register_command('help', self)
        self.register_command('?', self)
        self.register_command('verbose', self)
        readline.parse_and_bind("tab: complete")
        readline.set_completer(self.completer)

    def error(self, message):
        print(message)

    @property
    def prompt(self):
        return self.__prompt

    @prompt.setter
    def set_prompt(self, prompt):
        self.__prompt = prompt

    def input_loop(self):
        # ctrl D + exit
        line = ''
        while line != 'exit':
            try:
                line = input(self.prompt)
            except EOFError:
                # otherwise console will be on the same line
                print()
                sys.exit(0)
            except KeyboardInterrupt:
                print()
                sys.exit(0)

            self.dispatcher(line)

    def completer(self, text, state):
        # first complete commands
        # second delegate completer
        if state == 0:
            if type(text) == str:
                split = text.split(' ')
                if len(split) <= 1:
                    self.__completer = [s for s in self.__commands if s.startswith(split[0])]
                else:
                    if split[0] in self.__command:
                        self.__completer = self.__command[split[0]].complete(text)
                    else:
                        return None
            else:
                self.__completer = self.__commands
        try:
            return self.__completer[state] + " "
        except IndexError:
            return None

    def dispatcher(self, line):
        split = line.split(' ')
        cmd = split[0]
        argument = split[1:]
        if cmd in self.__command:
            self.__command[cmd].dispatch(cmd, argument)
        else:
            self.error("No such command. See help or ?")

    def register_command(self, name, cmdclass):
        # TODO: move this into class var of SubCommand
        self.__command[name] = cmdclass
        self.__commands.append(name)

    def dispatch(self, cmd, arg):
        """ self implemented commands """
        if cmd == "help" or cmd == "?":
            self.help()
        elif cmd == "verbose":
            self.verbose()

    def help(self):
        print("available commands : %s" % self.__commands)

    def verbose(self):
        logging.basicConfig()

class Cli(CliApp):
    def __init__(self, url, user, password):
        super().__init__()
        self.__url = url
        self.__user = user
        self.__password = password
        self.__ubus = JsonUbus(url, user, password)
        self.register_command('ubus', Ubus(self.__ubus))

class SubCommand(object):
    # todo class variables
    def complete(self, text):
        """ returns an array of possible extensions
            text is "cmd f"
            return ["cmd foo", "cmd fun", "cmd far"]
        """
        pass

    def dispatch(self, cmd, arguments):
        """ arguements is []
        """
        pass

class Ubus(SubCommand):
    """ Ubus calls foo """
    _commands = ['call', 'list']

    def __init__(self, ubus):
        self.__ubus = ubus
        self.__objects = {}
        self.__paths = []

    def update_paths(self):
        self.__paths = self.__ubus.list()

    def dispatch(self, cmd, arguments):
        # func obj <opt args depends on func type>
        argp = argparse.ArgumentParser(prog="ubus", description='Call ubus functions')
        argp.add_argument('func', nargs=1, type=str, help='list or call', choices=self._commands)
        argp.add_argument('path', nargs='?', type=str, help='ubus path')
        argp.add_argument('method', nargs='?', type=str, help='object function')
        self.update_paths()
        parsed, leftover = argp.parse_known_args(arguments)
        if parsed.func[0] == "call":
            if parsed.path == None:
                print('Path is missing')
            elif parsed.path not in self.__paths:
                print('Unknown path %s' % parsed.path)
            elif parsed.method is None:
                print('No method given!')
            else:
                self.__ubus.callp(parsed.path, parsed.method, **convert_to_dict(leftover))
        elif parsed.func[0] == 'list':
            if parsed.path:
                print(self.__ubus.list(parsed.path))
            else:
                print(self.__ubus.list())
        else:
            return 'Unknown ubus method {}'.format(parsed.func)

    def complete(self, text):
        split = text.split(' ')
        if len(split) > 1 and not split[0] in self._commands:
            # unknown command
            return
        if len(split) == 1:
            return [s for s in self._commands if s.startswith(split[0])]
        elif len(split) == 2:
            return [s for s in self.__objects if s.startswith(split[1])]
        elif len(split) == 3:
            pass

class Uci(SubCommand):
    pass

if __name__ == '__main__':
    Cli(url='http://127.0.0.1:8080/ubus', user='root', password='yipyip').input_loop()
