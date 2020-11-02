
# Entrypoint for readfs

import argparse
import os
import fs

LOOPBACK_FILE='/home/lmassa/loopbackfile.img'

def get_sb():
    state = "boot"
    with open(LOOPBACK_FILE, 'rb') as f:
        bl1 = f.read(0x400)
        bl2 = f.read(0x400)
        fs.validate_first_block(bl1)
        return fs.SuperBlock(bl2)

def show():
    sb = get_sb()
    sb.summarize()

def watch():
    prev_mtime = 0
    prev_sb = None
    while True:
        mtime = os.path.getmtime(LOOPBACK_FILE)
        if mtime > prev_mtime:
            sb = get_sb()
            if prev_sb is None or sb.raw_bytes != prev_sb.raw_bytes:
                print("Superblock updated!")
                sb.summarize()
            else:
                print("Filesystem updated, but superblock is the same")
            prev_sb = sb
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
