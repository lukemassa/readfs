# readfs
`readefs` is inspired by `readelf`, which takes an ELF binary, parses its internal binary structure, and displays it. `readfs` does the same for filesystems

## Implementation

`readfs` is written entirely in `python3` with no external dependencies.

## Use

`./readfs -h`

## Caveats
1. Currently only implemented for ext2
1. Currently only implemented for loopback devices (by inspecting the backing file)
1. Very inefficient, should only be used on small (MBs?) filesystems
