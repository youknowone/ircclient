# -*- coding: utf-8 -*-

import socket
from ircclient.socket import BlockingSocket as Socket


class MockSocket(Socket):

    def __init__(self, addr=('localhost', 8080), charset='utf-8'):
        Socket.__init__(self, addr, charset)

    def create_socket(self):
        self.socket = MockServerSocket()


class MockServerSocket(object):

    def __init__(self):
        self.buff = b''
        self.connected = False

    def connect(self, addr):
        self.buff += b':localhost NOTICE Auth :*** Looking up your hostname...\r\n'
        self.connected = True

    def send(self, line):
        cmds = line.split(b' ')
        table = {
            b'PING': b':localhost PONG ' + cmds[1],
            b'USER': b':localhost 375 the day of message',
            b'JOIN': b':localhost JOIN :blah',
            b'PART': b':localhost PART :blah',
            b'QUIT': b'ERROR :Closing link: (uname@14.36.48.145) [Quit: message]',
        }
        if cmds[0] in table:
            msg = table[cmds[0]] + b'\r\n'
            self.buff += msg
        if cmds[0] == b'QUIT':
            self.close()

    def recv(self, size):
        while len(self.buff) == 0:
            if not self.connected:
                raise socket.error(9, 'Bad descriptor')
        buff = self.buff
        self.buff = b''
        return buff

    def shutdown(self, how):
        self.connected = False

    def close(self):
        self.connected = False
