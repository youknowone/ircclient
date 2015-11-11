# -*- coding: utf-8 -*-
import pytest

from ircclient.socket import NonblockingSocket
from ircclient.struct import Message
from ircclient.const import PING, PONG, PRIVMSG, NOTICE, MODE, JOIN, PART

import settings

from mock_socket import MockSocket


@pytest.mark.parametrize(['SocketType'], [
    [NonblockingSocket],
    [MockSocket],
])
def test_create(SocketType):
    connop = settings.TEST_CONNECTION
    addr = (connop['host'], connop['port'])
    sock = SocketType(addr, 'utf-8')
    assert(sock.dispatch() is None)
    return sock

socktypes = [[MockSocket]]
if settings.TEST_REALSERVER:
    socktypes.append([NonblockingSocket])


@pytest.mark.parametrize(['NonblockingSocketType'], socktypes)
def test_enqueue(NonblockingSocketType):
    print(NonblockingSocketType)

    sock = test_create(NonblockingSocketType)
    sock.connect()
    for msg in sock.dispatch_all():
        print(msg)
        assert(msg == 'CONNECTED')
    assert(sock.dispatch() is None)

    def dispatch_useful():
        print('--> throwing out unusefuls')
        for msg in sock.dispatch_all():
            msg = Message(msg)
            print('type:', msg.type, 'msg:', u' '.join(msg).encode('utf-8'))
            if msg.type == PING:
                sock.send_args(PONG, msg[1])
                continue
            if msg.type == PRIVMSG:
                continue
            if msg.type == '375':
                break
            if len(msg.type) == 3 or msg.type in [NOTICE, MODE]:
                continue
            else:
                break
        else:
            print('<-- skipped all the trashes')
            return None
        print('<-- get a message')
        return msg

    sock.send_args('NICK', 'easybot')
    sock.send_args('USER', 'easybot', 'localhost', '0', 'realname')

    msg = None
    while msg is None:
        sock.recv()
        msg = dispatch_useful()
    assert(msg.type == '375')  # message of the day - for the registered user only

    connop = settings.TEST_CONNECTION
    chan = connop['autojoins'][0]
    sock.send_args(JOIN, chan)
    msg = None
    while msg is None:
        sock.recv()
        msg = dispatch_useful()
    assert(msg.type == JOIN)
    sock.send_args(PRIVMSG, chan, 'can you see my message?')
    sock.send_args(PRIVMSG, chan, u'can you see my 한글 message?')
    sock.send_args(PART, chan, u'test did end with non-ascii 한글')
    msg = None
    while msg is None:
        sock.recv()
        msg = dispatch_useful()
    assert(msg.type == 'PART')

if __name__ == '__main__':
    test_enqueue(MockSocket)
    if settings.TEST_REALSERVER:
        test_enqueue(NonblockingSocket)
