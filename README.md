This repository profiles memory footprint of Firecracker functions

This repo needs these mandatory components:
1. Firecracker binary
2. vmlinux
3. rootfs
4. workload

1 and 3 will be built by using Firecracker repo.
check out [docs](/docs/setup_node.md).


For `vmlinux`, we will use official Linux kernel image built by firecracker team. Replace `vmlinux` in [ubuntu](/ubuntu/) folder with the binary below.
```bash
latest=$(wget "http://spec.ccfc.min.s3.amazonaws.com/?prefix=firecracker-ci/v1.10/x86_64/vmlinux-5.10&list-type=2" -O - 2>/dev/null | grep "(?<=<Key>)(firecracker-ci/v1.10/x86_64/vmlinux-5\.10\.[0-9]{3})(?=</Key>)" -o -P)
wget https://s3.amazonaws.com/spec.ccfc.min/${latest}
```
