
# Entrypoint for readfs

import argparse
import os
import fs

LOOPBACK_FILE='/home/lmassa/loopbackfile.img'

def show(section):
    filesystem = fs.FileSystem(LOOPBACK_FILE)
    filesystem.parse()
    if section == "superblock":
        filesystem.superblock.summarize()
    elif section == "summary":
        filesystem.summarize()
    elif section == "group":
        filesystem.group_desc.summarize()
    else:
        raise ValueError("Unexpected section %s" % (section))

def watch(section):
    prev_mtime = 0
    prev_sb = None
    while True:
        mtime = os.path.getmtime(LOOPBACK_FILE)
        if mtime > prev_mtime:
            show(section)
            prev_mtime = mtime


def main():

    parser = argparse.ArgumentParser()
    parser.add_argument("section", choices=["summary", "superblock", "group"])
    parser.add_argument("action", choices=["show", "watch"])
    args = parser.parse_args()

    if args.action == "show":
        show(args.section)
    elif args.action == "watch":
        watch(args.section)

if __name__ == "__main__":
    main()
