
# These functions might be defined elsewhere but I wanted to be explicit
import uuid


def parse_16(word):
    assert len(word) == 2
    return int(word[0]) + 256 * int(word[1])

def parse_32(word):
    assert len(word) == 4
    return parse_16(word[:2]) + 256*256* parse_16(word[2:])

def parse_uuid(word):
    assert len(word) == 16
    return str(uuid.UUID(bytes=word))

def parse_char(word):
    return word.decode('ascii')
