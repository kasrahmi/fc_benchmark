UFFD_SOCKET="/tmp/firecracker-uffd.socket"
TAP_DEV="tap0"
TAP_IP="192.168.0.1"
MASK_SHORT="/30"

# Setup network interface
sudo ip link del "$TAP_DEV" 2> /dev/null || true
sudo ip tuntap add dev "$TAP_DEV" mode tap
sudo ip addr add "${TAP_IP}${MASK_SHORT}" dev "$TAP_DEV"
sudo ip link set dev "$TAP_DEV" up

# Enable ip forwarding
sudo sh -c "echo 1 > /proc/sys/net/ipv4/ip_forward"

HOST_IFACE="eno1"

# Set up microVM internet access
sudo iptables -t nat -D POSTROUTING -o "$HOST_IFACE" -j MASQUERADE || true
sudo iptables -D FORWARD -m conntrack --ctstate RELATED,ESTABLISHED -j ACCEPT \
    || true
sudo iptables -D FORWARD -i tap0 -o "$HOST_IFACE" -j ACCEPT || true
sudo iptables -t nat -A POSTROUTING -o "$HOST_IFACE" -j MASQUERADE
sudo iptables -I FORWARD 1 -m conntrack --ctstate RELATED,ESTABLISHED -j ACCEPT
sudo iptables -I FORWARD 1 -i tap0 -o "$HOST_IFACE" -j ACCEPT

sleep 5s

# setup custom uffd handler
tmux kill-session -t uffd_handler
sudo rm /tmp/firecracker-uffd.socket
tmux new -s uffd_handler -d
# tmux send -t uffd_handler "sudo ./bin/uffd_valid_count_periodic_handler ${UFFD_SOCKET} ./snapshot/mem_file" ENTER
tmux send -t uffd_handler "sudo ./bin/uffd_valid_count_handler ${UFFD_SOCKET} ./snapshot/mem_file" ENTER

# sudo ./uffd_valid_count_periodic_handler "${UFFD_SOCKET}" ./snapshot/mem_file &
# tmux attach -t uffd_handler

sleep 5s

# load snapshot with uffd
echo "load snapshot"
sudo curl --unix-socket /tmp/firecracker.socket -i \
    -X PUT 'http://localhost/snapshot/load' \
    -H  'Accept: application/json' \
    -H  'Content-Type: application/json' \
    -d '{
            "snapshot_path": "./snapshot/snapshot_file",
            "mem_backend": {
                "backend_path": "/tmp/firecracker-uffd.socket",
                "backend_type": "Uffd"
            },
            "enable_diff_snapshots": false,
            "resume_vm": false
    }'

sleep 5s

# resume snapshot with uffd
echo "resume vm"
sudo curl --unix-socket /tmp/firecracker.socket -i \
    -X PATCH 'http://localhost/vm' \
    -H 'Accept: application/json' \
    -H 'Content-Type: application/json' \
    -d '{
            "state": "Resumed"
    }'
