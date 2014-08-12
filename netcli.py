#!/usr/bin/env python3

from .jsonubus import JsonUbus

class CliApp(object):
    def __init__(self):
        self.__prompt = None
        self.__command = {}
        self.__commands = []
        self.__completer = []

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
            line = input(self.prompt)
            self.dispatch(line)

    def completer(self, text, state):
        # first complete commands
        # second delegate completer
        if state == 0:
            if text:
                split = text.split(' ')
                if len(split) <= 1:
                    self.__completer = [s for s in self.__commands if text.startswith(s)]
                else:
                    self.__completer = self.__command[split[0]].complete(text)
            else:
                self.__completer = self.__commands

        try:
            return self.__completer[state]
        except IndexError:
            return None

    def dispatch(self, line):
        split = line.split(' ')
        cmd = split[0]
        argument = split[1:]
        if cmd in self.__command:
            self.__command[cmd].dispatch(cmd, argument)

    def register_command(self, name, cmdclass):
        self.__command[name] = cmdclass
        self.__commands.append(name)

class Cli(CliApp):
    def __init__(self, url, user, password):
        super().__init__()
        self.__url = url
        self.__user = user
        self.__password = password
        self.__ubus = JsonUbus(url, user, password)

class SubCommand(object):
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

