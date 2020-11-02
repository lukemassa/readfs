#!/usr/bin/python3

import sys
import re
import os
import subprocess
import byte_parser


# For parsing c-structs like: '     __le32  s_inodes_count;     /* Inodes count */'
STRUCT_LINE_RE = re.compile(r"^ +([a-z0-9_]+) +([a-z_]+)(?:\[([0-9]+)\])?; +\/\* (.*) \*\/$")

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
            "superblock" : self.parse_struct("conf/superblock"),
            "group_desc" : self.parse_struct("conf/group_desc"),
        }

    @property
    def superblock(self):
        return self._blocks[1]

    @property
    def group_desc(self):
        # There might be more than one group!
        return self._blocks[2]


    @staticmethod
    def parse_struct(filename):
        ret = []
        with open(filename) as f:
            for line in f.read().split('\n'):
                if not line:
                    continue
                if line[0] == "#":
                    continue
                parsed_line = STRUCT_LINE_RE.match(line)
                if parsed_line is None:
                    raise ValueError("Unexpected line in struct: %s" % (line,))
                ret.append({
                    "type" : parsed_line.group(1),
                    "var" : parsed_line.group(2),
                    "length" : parsed_line.group(3),
                    "comment" : parsed_line.group(4)
                })
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
            blocks.append(Block(f.read(BLOCK_SIZE)))
            blocks[0].make_empty_block()

            blocks.append(Block(f.read(BLOCK_SIZE)))
            blocks[1].make_super_block(self._structs["superblock"])

            blocks.append(Block(f.read(BLOCK_SIZE)))
            blocks[2].make_group_desc_block(self._structs["group_desc"])

            while True:
                raw_bytes = f.read(BLOCK_SIZE)
                if not raw_bytes:
                    break
                block = Block(raw_bytes)
                if block.is_all_zeroes():
                    block.make_empty_block()
                blocks.append(block)

        self._blocks = blocks

    def summarize(self):
        for block in self._blocks:
            sys.stdout.write(block.letter)
        sys.stdout.write("\n")

class Block:

    letter = '?'

    def __init__(self, raw_bytes):

        self.raw_bytes = raw_bytes

    def make_super_block(self, struct):
        self.letter ='S'
        self.parse(struct)

    def make_empty_block(self):
        self.letter = ' '
        if not self.is_all_zeroes():
            raise ValueError("Attempting to make empty block from non-zeroed block")

    def make_group_desc_block(self, struct):
        self.letter = 'G'
        self.parse(struct)

    def parse(self, struct):
        ret = {}
        i = 0
        for entry in struct:
            if entry["type"] == "__le16":
                ret[entry["comment"]] = byte_parser.parse_16(self.raw_bytes[i:i+2])
                i+=2
            elif entry["type"] == "__le32":
                ret[entry["comment"]] = byte_parser.parse_32(self.raw_bytes[i:i+4])
                i+=4
            elif entry["type"] == "uuid":
                ret[entry["comment"]] = byte_parser.parse_uuid(self.raw_bytes[i:i+16])
                i+=16
            elif entry["type"] == "char":
                length = int(entry["length"])
                ret[entry["comment"]] = byte_parser.parse_char(self.raw_bytes[i:i+length])
                i+=length
            else:
                raise ValueError("Unexpected value %s" % (entry["type"]))
        self.state = ret

    def summarize(self):
        if self.is_all_zeroes():
            print("Empty block!")
            return
        if self.letter == 'S':
            print("Super block:")
        if self.letter == 'G':
            print("Group description")
        for k, v in self.state.items():
            print("  %s: %s" % (k, v))
                        
    def is_all_zeroes(self):
        for byte in self.raw_bytes:
            if byte != 0:
                return False
        return True
