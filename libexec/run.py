
# Entrypoint for readfs

import argparse
import os
import fs

LOOPBACK_FILE='/home/lmassa/loopbackfile.img'

def show():
    filesystem = fs.FileSystem(LOOPBACK_FILE)
    filesystem.parse()
    filesystem.superblock.summarize()

def watch():
    prev_mtime = 0
    prev_sb = None
    while True:
        mtime = os.path.getmtime(LOOPBACK_FILE)
        if mtime > prev_mtime:
            show()
            prev_mtime = mtime


def main():

    parser = argparse.ArgumentParser()
    parser.add_argument("action", choices=["show", "watch"])
    args = parser.parse_args()

    if args.action == "show":
        show()
    elif args.action == "watch":
        watch()

if __name__ == "__main__":
    main()
