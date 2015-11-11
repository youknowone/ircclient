# -*- coding: utf-8 -*-
from __future__ import absolute_import

import socket
import select

from .const import CONNECTED, DISCONNECTED, CREATED


RAW_LOG = False


class BaseSocket(object):

    def __init__(self, addr, charset='utf-8'):
        """addr is a tuple represents (host, port)"""
        self.addr = addr
        self.charset = charset
        self._buffer = b''
        self.recv_queue = []
        self.send_queue = []
        self.send_callback = None

        self.connected = None
        self.create_socket()

    def create_socket(self):
        """Override to change internal socket."""
        self.socket = socket.socket()

    def send(self, string):
        if self.send_callback:
            self.send_callback(string)
        assert string.endswith('\r\n')
        self._send(string)

    def _send(self, string):
        raise NotImplementedError

    def connect(self):
        self.recv_queue.append(CONNECTED)  # EVERYTHING-IS-RESPONSE!
        self.connected = True
        raise NotImplementedError

    def disconnect(self):
        self.recv_queue.append(DISCONNECTED)  # EVERYTHING-IS-RESPONSE!
        raise NotImplementedError

    def _recv(self):
        raise NotImplementedError

    def send_line(self, line, *arg, **kwargs):
        if len(arg) or len(kwargs):
            line = line.format(*arg, **kwargs)
        # print '--> SEND', line
        self.send(line + '\r\n')

    def send_args(self, *args):
        self.send_list(args)

    def send_list(self, items):
        items = list(items)[:-1] + [':' + items[-1]]
        line = u' '.join(items)
        self.send_line(line)

    def needs_dispatch(self):
        return not self.recv_queue

    def dispatch(self):
        """Dispatch an item from recv_queue."""
        if not self.recv_queue:
            return None
        msg = self.recv_queue.pop(0)
        if RAW_LOG:
            print('>', msg)
        return msg

    def dispatch_all(self):
        msg = True
        while msg:
            msg = self.dispatch()
            if msg:
                yield msg
        raise StopIteration

    def _split_buffer(self):
        """Catch 'ValueError' to check unsplitable"""
        newline, self._buffer = self._buffer.split(b'\r\n', 1)
        try:
            return newline.decode(self.charset)
        except:
            print('Supposed charset is', self.charset, ', but undecodable string found:', newline)
            return newline

    def _enqueue(self, line):
        self.recv_queue.append(line)

    def _enqueue_buffer(self):
        try:
            while True:
                newline = self._split_buffer()
                self._enqueue(newline)
        except ValueError:
            pass

    def recv(self, wait_enqueue=False):
        while True:
            try:
                recv = self._recv()
                if recv is None:
                    if wait_enqueue:
                        continue
                    else:
                        break
                if recv == '':
                    raise socket.error("recv() returned an empty string")
                self._buffer += recv
                self._enqueue_buffer()
            except Exception as e:
                if isinstance(e, socket.error):
                    self.recv_queue.append(DISCONNECTED)
                    self.connected = False
                else:
                    import traceback
                    print('--- Error caught ---')
                    traceback.print_exc()
                    raise e  # debug
                self._enqueue(e)
            if not wait_enqueue or len(self.recv_queue) > 0:
                break


class BlockingSocket(BaseSocket):

    def _send(self, line):
        if RAW_LOG:
            print('<', line,)
        self.socket.send(line.encode(self.charset))

    def connect(self):
        self.socket.connect(self.addr)
        self.recv_queue.append(CONNECTED)  # EVERYTHING-IS-RESPONSE!
        self.connected = True

    def disconnect(self):
        # self.socket.shutdown(socket.SHUT_RDWR)
        self.socket.close()

    def _recv(self):
        """NOTE: blocking"""
        return self.socket.recv(1024)  # 1kb is enough for irc


class NonblockingSocket(BaseSocket):

    def send(self, line):
        self.send_queue.append(line)

    def connect(self):
        self.socket.connect(self.addr)
        self.recv_queue.append(CONNECTED)  # EVERYTHING-IS-RESPONSE!
        self.connected = True
        self.socket.setblocking(0)

    def disconnect(self):
        # self.socket.shutdown(socket.SHUT_RDWR)
        self.socket.close()

    def _recv(self):
        if self.send_queue:
            read, write, error = select.select([], [self.socket], [], 0.1)
            if write:
                line = self.send_queue.pop(0)
                if self.send_callback:
                    self.send_callback(line)
                write[0].send(line.encode(self.charset))

        read, write, error = select.select([self.socket], [], [], 0.1)
        if read:
            return read[0].recv(1024)  # 1kb is enough for irc
        else:
            return None


class NoneSocket(BaseSocket):

    def __init__(self, addr, charset='utf-8'):
        self.connected = None

        BaseSocket.__init__(self, addr, charset)

    def dispatch(self):
        return CREATED


class ClosedSocket(BaseSocket):

    def __init__(self, addr, charset='utf-8'):
        self.connected = False

        BaseSocket.__init__(self, addr, charset)

    def dispatch(self):
        return DISCONNECTED
