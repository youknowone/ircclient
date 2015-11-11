# -*- coding: utf-8 -*-
from __future__ import absolute_import

import threading

from .struct import Message
from .socket import BlockingSocket, NonblockingSocket, ClosedSocket, NoneSocket


class BaseClient(object):
    """
    Common IRC client interface.
    Any client should support:
        self.socket: any ircclient.socket
    """

    def __init__(self, addr, **kwargs):
        blocking = kwargs.get('blocking', True)
        SocketClass = BlockingSocket if blocking else NonblockingSocket
        self.socket = SocketClass(addr)
        self._message_queue = []
        self.options = kwargs
        self.quitting = False

    def runloop_unit(self):
        raise NotImplementedError

    def enqueue(self, msg):
        self._message_queue.append(msg)

    def dispatchable(self):
        return self._message_queue or not self.socket.needs_dispatch()

    def dispatch(self, raw=False):
        """Get a message from socket."""
        if self._message_queue:
            message = self._message_queue.pop(0)
        else:
            message = self.socket.dispatch()
        if message is not None and not raw:
            message = Message(message)
        return message

    def run(self):
        """Thread loop."""
        while self.socket.connected is not False:
            self.runloop_unit()

    def start(self):
        self.thread = threading.Thread()
        self.thread.run = self.run
        self.thread.start()

    def connect(self):
        self.socket.connect()

    def disconnect(self):
        self.socket.disconnect()
        self.socket = ClosedSocket(('', 0))

    def reconnect(self):
        self.socket = NoneSocket()

    def __getattr__(self, key):
        """Borrow commands from command manager."""
        if key.startswith('send_'):
            attr = getattr(self.socket, key)
            return attr
        return self.__getattribute__(key)

    def __call__(self, *args, **kwargs):
        if isinstance(args[0], list):
            self.send_list(args[0])
        else:
            if len(args) == 1:
                if kwargs:
                    line = args[0].format(*args[1:], **kwargs)
                else:
                    line = args[0]
                self.send_line(line)
            else:
                self.send_args(*args)


class DispatchClient(BaseClient):
    """Client implementation based on manual dispatching."""

    def runloop_unit(self):
        """NOTE: blocking"""
        self.socket.recv()


class CallbackClient(BaseClient):
    """Callback-driven IRC client"""

    def __init__(self, addr, callback, options=None):
        self.callback = callback

        BaseClient.__init__(self, addr, options=None)

    def runloop_unit(self):
        """NOTE: blocking"""
        msg = self.dispatch()
        if msg is not None:
            self.callback(self, msg)
        else:
            self.socket.recv()
