UFFD_SOCKET="/tmp/firecracker-uffd.socket"

tmux kill-session -t fc_uffd
sudo rm -f $UFFD_SOCKET

tmux new -s fc_uffd -d

tmux send -t fc_uffd "./bin/uffd_valid_count_handler ${UFFD_SOCKET} ./snapshot/mem_file" ENTER