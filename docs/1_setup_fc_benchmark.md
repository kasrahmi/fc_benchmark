# Setup FC_Benchmark Repository

### Setup Firecracker Binary, Ubuntu RootFS, and vmlinux

```bash
bash scripts/build_toolchain.sh
```

### Get vmlinux

*Since we are using Linux 6.1, we need to build our own. **Do NOT** run this unless you are using 5.10.*

For `vmlinux`, we will use official Linux kernel image built by firecracker team. Replace `vmlinux` in [ubuntu](/ubuntu/) folder with the binary below.
```bash
latest=$(wget "http://spec.ccfc.min.s3.amazonaws.com/?prefix=firecracker-ci/v1.10/x86_64/vmlinux-5.10&list-type=2" -O - 2>/dev/null | grep "(?<=<Key>)(firecracker-ci/v1.10/x86_64/vmlinux-5\.10\.[0-9]{3})(?=</Key>)" -o -P)
wget https://s3.amazonaws.com/spec.ccfc.min/${latest}
```



### Set Ethernet Dev of Firecracker VM
Inside `scripts/run_fc.sh`, set `HOST_IFACE` value to appropriate device. Use `ifconfig` to find the device that connects to ethernet.

```bash
HOST_IFACE="eno49np0"
```
