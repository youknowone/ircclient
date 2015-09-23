
# -*- coding: utf-8 -*-
import pytest

from ircclient.struct import Message, Identity


@pytest.mark.parametrize(['line', 'items'], [
    [u':localhost PING :thepingstring', ['localhost', 'PING', 'thepingstring']],
    [u'PRIVMSG #chan nick :this is the msg', [None, 'PRIVMSG', '#chan', 'nick', 'this is the msg']],
])
def test_msgsplit(line, items):
    splited = Message(line)
    assert splited == items


@pytest.mark.parametrize(['sender', 'nick', 'username', 'host'], [
    [u'userident!~ircclient@127.0.0.1', 'userident', '~ircclient', '127.0.0.1'],
])
def test_identify(sender, nick, username, host):
    identity = Identity(sender)
    assert identity.nick == nick
    assert identity.username == username
    assert identity.host == host
