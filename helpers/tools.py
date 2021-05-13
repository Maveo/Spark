def from_char(c):
    return ''.join(['{:x}'.format(x) for x in c.encode('utf-8')])


def to_char(c):
    return bytes.fromhex(c).decode('utf-8')
