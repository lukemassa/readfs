#!/usr/bin/python3

import sys
import re
import os
import subprocess
import byte_parser


# For parsing c-structs like: '     __le32  s_inodes_count;     /* Inodes count */'
STRUCT_LINE_RE = re.compile(r"^ +([a-z0-9_]+) +([a-z_]+); +\/\* (.*) \*\/$")

# TODO: Parameterize this
BLOCK_SIZE=0x400

def validate_first_block(bl):
    assert len(bl) == 1024
    for byte in bl:
        assert byte == 0


def shell(args):
    """Executes a shell command
    """
    if isinstance(args, str):
        raise ValueError("Passed string to shell, it is safer to use array: %s" % args)

    proc = subprocess.Popen(args, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    out, err = proc.communicate()
    ret = proc.returncode

    out = str(out.decode())
    err = str(err.decode())


    return (ret, out, err)


class FileSystem:

    def __init__(self, path):
        self.assert_is_fs(path)
        self.path = path
        self._blocks = []

        self._structs = {
            "superblock" : self.parse_struct("conf/superblock")
        }

    @property
    def superblock(self):
        return self._blocks[1]


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
    def assert_is_fs(path):
        res, out, err = shell(["file", path])
        if res != 0:
            raise ValueError("Error running file %s: %s" % (path, err))
        if "filesystem data" not in out:
            raise ValueError("File %s is not a filesystem: %s" % (path, out))
        if "ext2" not in out:
            raise ValueError("Currently only supporting ext2, found %s" % (out,))

    
    def parse(self):
        blocks = []
        state = "boot"
        with open(self.path, 'rb') as f:
            blocks.append(EmptyBlock(f.read(0x400), None).init())
            blocks.append(SuperBlock(f.read(0x400), self._structs["superblock"]).init())
        self._blocks = blocks

class Block:

    letter = '?'

    def __init__(self, raw_bytes, struct):
        self.struct = struct

        self.raw_bytes = raw_bytes

    def init(self):
        return self

    def parse(self):
        ret = {}
        i = 0
        for entry in self.struct:
            if entry[0] == "__le16":
                ret[entry[2]] = byte_parser.parse_16(self.raw_bytes[i:i+2])
                i+=2
            elif entry[0] == "__le32":
                ret[entry[2]] = byte_parser.parse_32(self.raw_bytes[i:i+4])
                i+=4
            else:
                raise ValueError("Unexpected value %s" % (entry[0]))
        self.state = ret

    def summarize(self):
        print("Super block:")
        for k, v in self.state.items():
            print("  %s: %s (%s)" % (k, v, hex(v)))
                        

class SuperBlock(Block):

    letter = 'S'

    def init(self):
        self.parse()
        return self

class EmptyBlock(Block):
    letter = ' '

    def init(self):
        assert len(self.raw_bytes) == 1024
        for byte in self.raw_bytes:
            assert byte == 0
        return self
