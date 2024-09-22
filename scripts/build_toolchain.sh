./../firecracker/tools/devtool build
cp ../firecracker/build/cargo_target/x86_64-unknown-linux-musl/debug/firecracker bin/.
cp ../firecracker/build/cargo_target/x86_64-unknown-linux-musl/debug/examples/uffd_valid_count_periodic_handler bin/.
cp ../firecracker/build/cargo_target/x86_64-unknown-linux-musl/debug/examples/uffd_valid_count_handler bin/.


bash ../firecracker/resources/rebuild.sh
cp ../firecracker/resources/x86_64/* ubuntu/.


ssh-keygen -f "/users/nehalem/.ssh/known_hosts" -R "192.168.0.2"