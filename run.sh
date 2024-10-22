# go run ./go_profiling -l python -e helloworld_vsock --loop 10 --profiling stable
# go run ./go_profiling -l python -e helloworld_vsock --loop 10 --profiling reap
# go run ./go_profiling -l python -e helloworld_tcp --loop 10 --profiling stable
# go run ./go_profiling -l python -e helloworld_tcp --loop 10 --profiling reap
# go run ./go_profiling -l python -e helloworld_grpc --loop 10 --profiling stable
# go run ./go_profiling -l python -e helloworld_grpc --loop 10 --profiling reap
# go run ./go_profiling -l python -e aes --loop 10 --profiling stable
# go run ./go_profiling -l python -e aes --loop 10 --profiling reap
# go run ./go_profiling -l python -e lr_serving --loop 10 --profiling stable
# go run ./go_profiling -l python -e lr_serving --loop 10 --profiling reap


go run ./go_profiling -l python -e helloworld_neta --loop 10 --profiling stable
go run ./go_profiling -l python -e helloworld_neta --loop 10 --profiling reap
go run ./go_profiling -l python -e helloworld_s3 --loop 10 --profiling stable
go run ./go_profiling -l python -e helloworld_s3 --loop 10 --profiling reap