
# -*- coding: utf-8 -*-
import time
import pytest
from ircclient.client import DispatchClient, CallbackClient
from ircclient.const import *
from ircclient.struct import Message
from mock_socket import MockSocket

from test_socket import socktypes, test_create

import settings
connop = settings.TEST_CONNECTION


@pytest.mark.parametrize(['SocketType'], socktypes)
def test_dispatch(SocketType):
    client = DispatchClient(None)
    msg = client.dispatch()
    assert msg is None
    client.socket = test_create(SocketType)
    assert client.socket.recv_queue == []
    client.connect()
    assert client.socket.recv_queue == [CONNECTED]
    msg = client.dispatch()
    assert msg.type == CONNECTED

    def check_msg(themsg):
        while True:
            time.sleep(0.1)
            client.runloop_unit()
            msg = client.dispatch()
            if msg is None:
                continue
            if msg.type == PING:
                client.pong(msg[1])
                continue
            if msg.type == themsg:
                break
            else:
                print msg

    client(NICK, connop['nick'])
    client.send_args(USER, connop['nick'], 'Bot by EasyIRC')
    check_msg('375')

    client(JOIN, connop['autojoins'][0])
    check_msg(JOIN)

    client(PART, connop['autojoins'][0])
    check_msg(PART)

    client(QUIT, u'QUIT MESSAGE')
    check_msg('ERROR')
    client.disconnect()


@pytest.mark.parametrize(['SocketType'], socktypes)
def test_callback(SocketType):
    print SocketType

    def callback(client, ps):
        chan = connop['autojoins'][0]
        if ps.type == CONNECTED:
            client(NICK, connop['nick'])
            client(USER, connop['nick'], 'Bot by EasyIRC')
        elif ps.type == PING:
            client(PONG, ps[1])
        elif ps.type == '375':
            client(JOIN, chan)
        elif ps.type == JOIN:
            client(PRIVMSG, chan, u'test the 콜백')
            client(QUIT, u'전 이만 갑니다')
        elif ps.type == 'ERROR':
            print 'END!'
            client.disconnect()
        else:
            print ps

    client = CallbackClient(None, callback)

    client.socket = test_create(SocketType)
    client.connect()
    while client.socket.connected:
        client.runloop_unit()


if __name__ == '__main__':
    test_dispatch(socktypes[0][0])
    # test_dispatch(socktypes[1][0])
    test_callback(socktypes[0][0])
    # test_callback(socktypes[1][0])
