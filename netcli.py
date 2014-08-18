#!/usr/bin/env python3

from jsonubus import JsonUbus
import readline
import logging
import sys

LOG = logging.getLogger('netcli')

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
            self.__command[cmd].dispatch(cmd, line[len(cmd)+1:])

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

class SubCommand(object):
    # todo class variables
    def complete(self, text):
        """ returns an array of possible extensions
            text is "cmd f"
            return ["cmd foo", "cmd fun", "cmd far"]
        """
        pass

    def dispatch(self, arguments):
        pass

class Ubus(SubCommand):
    pass

class Uci(SubCommand):
    pass

if __name__ == '__main__':
    Cli(url='http://127.0.0.1:8080/ubus', user='root', password='yipyip').input_loop()
