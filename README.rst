.. image:: https://travis-ci.org/youknowone/ircclient.svg?branch=master
    :target: https://travis-ci.org/youknowone/ircclient

ircclient
~~~~~~~~~

Simple IRC client interface.


Example
-------

.. code:: python

    from ircclient.client import DispatchClient

    client = DispatchClient(('localhost', 6667), blocking=True)
    client.connect()

    m = client.dispatch()  # ircclient.struct.Message
    assert m.type == 'CONNECTED'  # connected message which is out of irc protocol

    client('nick', 'testnick')  # list args are joined. colons will be automatically added.
    client('user 8 * :{name}', name='realname')  # keyword args are formatted as raw string

    while True:
        m = client.dispatch()  # raw=True option will make it returns raw text
        print(m)  # ircclient.struct.Message


