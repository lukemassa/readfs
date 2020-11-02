## readfs
`readefs` is inspired by `readelf`, which takes an ELF binary, parses its internal binary structure, and displays it. `readfs` does the same for filesystems

### Caveats
1. Currently only implemented for ext2
1. Currently only implemented for loopback devices (by inspecting the backing file)
1. Very inefficient, should only be used on small (MBs?) filesystems
