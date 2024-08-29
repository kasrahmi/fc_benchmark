API_SOCKET="/tmp/firecracker.socket"

# Remove API unix socket
sudo rm -f $API_SOCKET

tmux kill-session -t fc_vmm
tmux new -s fc_vmm -d

tmux send -t fc_vmm "sudo ./bin/firecracker --api-sock ${API_SOCKET}" ENTER