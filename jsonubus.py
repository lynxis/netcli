#!/usr/bin/env python3

import json
import jsonrpclib
import logging

class Ubus(object):
    def list(self, path):
        raise NotImplementedError

    def call(self, path, func, params):
        raise NotImplementedError

    def subscribe(self, path):
        raise NotImplementedError

class JsonUbus(Ubus):
    def __init__(self, url, user, password):
        self.url = url
        self._server = jsonrpclib.ServerProxy(self.url)
        self.__session = None
        self.__user = user
        self.__password = password
        self.__timeout = None
        self.__expires = None
        self.logger = logging.getLogger('jsonubus')

    def session(self):
        if self.__session == None:
            ret = self._server.call("00000000000000000000000000000000", "session", "login", {"username": self.__user, "password": self.__password})
            self.__session = ret[1]['ubus_rpc_session']
            self.__timeout = ret[1]['timeout']
            self.__expires = ret[1]['expires']
            self.logger.warn('Connected with %s' % self.url)
        return self.__session

    def list(self, path=None):
        if path:
            return self._server.list(path)
        else:
            return self._server.list()

    def call(self, path, func, params=None):
        if params:
            if type(params) is not dict:
                raise RuntimeError("Wrong params type. %s != dict" % type(params))
            self._server.call(self.session(), path, func, params)
        else:
            self._server.call(self.session(), path, func, {})
