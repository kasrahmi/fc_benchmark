sudo timeout 10s perf stat -e task-clock,cycles,instructions,cache-references,cache-misses,minor-faults,major-faults,page-faults,L1-dcache-loads,L1-dcache-load-misses,L1-dcache-stores,L1-dcache-store-misses python server.py --host 172.16.0.2 --port 65432

sudo timeout 10s perf record -e task-clock,cycles,instructions,cache-references,cache-misses,minor-faults,major-faults,page-faults,L1-dcache-loads,L1-dcache-load-misses,L1-dcache-stores python greeter_server_local.py

python client.py --host 127.0.0.1 --port 65432 --name John

while true; do python greeter_client_local.py; sleep 2; done;

while true; do python client.py --host 127.0.0.1 --port 65432 --name John; sleep 2; done;

sudo perf report

rsync -Pav -e "ssh -i /users/nehalem/firecracker/profiling/ubuntu/ubuntu-22.04.id_rsa" greeter_server_tcp root@172.16.0.2:/root/.

# use perf stat than perf record

./greeter_server_tcp --target 172.16.0.2:50051
./greeter_client_tcp --target 172.16.0.2:50051

./greeter_server --target 172.16.0.2:50051
./greeter_client --target 172.16.0.2:50051