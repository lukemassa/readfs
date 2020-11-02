#!/usr/bin/python3

import sys
import re
import os

# For parsing c-structs like: '     __le32  s_inodes_count;     /* Inodes count */'
STRUCT_LINE_RE = re.compile(r"^ +([a-z0-9_]+) +([a-z_]+); +\/\* (.*) \*\/$")

def validate_first_block(bl):
    assert len(bl) == 1024
    for byte in bl:
        assert byte == 0

class Block:

    def __init__(self, raw_bytes):
        self.struct = self.parse_struct("conf/superblock")

        self.raw_bytes = raw_bytes
        self.state= self.parse()

    @staticmethod
    def parse_struct(filename):
        ret = []
        with open(filename) as f:
            for line in f.read().split('\n'):
                if not line:
                    continue
                parsed_line = STRUCT_LINE_RE.match(line)
                if parsed_line is None:
                    raise ValueError("Unexpected line in struct: %s" % (line,))
                ret.append(parsed_line.groups())
        return ret

    @staticmethod
    def _parse_16(word):
        assert len(word) == 2
        return int(word[0]) + 256 * int(word[1])

    @staticmethod
    def _parse_32(word):
        assert len(word) == 4
        return SuperBlock._parse_16(word[:2]) + 256*256* SuperBlock._parse_16(word[2:])

    def parse(self):
        ret = {}
        i = 0
        for entry in self.struct:
            if entry[0] == "__le16":
                ret[entry[2]] = self._parse_16(self.raw_bytes[i:i+2])
                i+=2
            elif entry[0] == "__le32":
                ret[entry[2]] = self._parse_32(self.raw_bytes[i:i+4])
                i+=4
            else:
                raise ValueError("Unexpected value %s" % (entry[0]))
        return ret

    def summarize(self):
        print("Super block:")
        for k, v in self.state.items():
            print("  %s: %s (%s)" % (k, v, hex(v)))
                        

class SuperBlock(Block):

    def __init__(self, raw_bytes):
        self.struct = self.parse_struct("conf/superblock")

        self.raw_bytes = raw_bytes
        self.state= self.parse()
