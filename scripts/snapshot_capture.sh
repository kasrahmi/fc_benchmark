API_SOCKET="/tmp/firecracker.socket"
UFFD_SOCKET="/tmp/firecracker-uffd.socket"

# Pause vm for snapshotting

curl --unix-socket "${API_SOCKET}" -i \
-X PATCH 'http://localhost/vm' \
    -H 'Accept: application/json' \
    -H 'Content-Type: application/json' \
    -d '{
            "state": "Paused"
    }'

sleep 1s

# Cleanup snapshot and mem_file
# sudo rm ./snapshot/snapshot_file ./snapshot/mem_file

sleep 1s


# Capture full snapshot
curl --unix-socket "${API_SOCKET}" -i \
    -X PUT 'http://localhost/snapshot/create' \
    -H  'Accept: application/json' \
    -H  'Content-Type: application/json' \
    -d '{
            "snapshot_type": "Full",
            "snapshot_path": "./snapshot/snapshot_file",
            "mem_file_path": "./snapshot/mem_file"
    }'

# # Capture diff snapshot
# curl --unix-socket "${API_SOCKET}" -i \
#     -X PUT 'http://localhost/snapshot/create' \
#     -H  'Accept: application/json' \
#     -H  'Content-Type: application/json' \
#     -d '{
#             "snapshot_type": "Diff",
#             "snapshot_path": "./snapshot/snapshot_file",
#             "mem_file_path": "./snapshot/mem_file"
#     }'



sleep 1s

# resume paused vm

curl --unix-socket "${API_SOCKET}" -i \
    -X PATCH 'http://localhost/vm' \
    -H 'Accept: application/json' \
    -H 'Content-Type: application/json' \
    -d '{
            "state": "Resumed"
    }'
