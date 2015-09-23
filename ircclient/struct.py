
class ArgumentList(object):

    def __init__(self, owner, base_index=0):
        self.owner = owner
        self.base_index = base_index

    def __getitem__(self, index):
        return self.owner[self.base_index + index]


class Message(list):

    def __init__(self, line, raw=True):
        """General IRC message decoder"""
        if not raw:
            super(Message, self).__init__(line)
        else:
            super(Message, self).__init__()
            assert isinstance(line, unicode)

            # Append the sender, if not exists
            if line[0] == ':':
                item, line = line.split(' ', 1)
                self.append(decolon(item))
            else:
                self.append(None)

            self += Command(line)

        self.args = ArgumentList(self, 1)

    @property
    def sender(self):
        return self[0]

    @property
    def nick(self):
        return self[0].split('!', 1)[0]

    @property
    def type(self):
        return self[1]


class Command(list):

    def __init__(self, line, raw=True):
        """General IRC message decoder"""
        if not raw:
            super(Command, self).__init__(line)
        else:
            super(Command, self).__init__()

            while ' ' in line:
                # Colon-headed item means it is long argument
                if line[0] == ':':
                    break
                item, line = line.split(' ', 1)
                # Skip zero-lengthed item - split is not good enough for this case
                if len(item) == 0:
                    continue
                self.append(decolon(item))
            # Attach the last item
            self.append(decolon(line))

        self.args = ArgumentList(self, 0)

    @property
    def cmd(self):
        return self[0]

    @classmethod
    def interpret(cls, line):
        items = cls()


class Identity(unicode):

    @property
    def nick(self):
        return self.split('!', 1)[0]

    @property
    def username(self):
        return self.split('@', 1)[0].split('!', 1)[1]

    @property
    def host(self):
        return self.split('@', 1)[1]


def decolon(item):
    """Colon has special usage in IRC protocol"""
    if item[0] == ':':
        return item[1:]
    return item
