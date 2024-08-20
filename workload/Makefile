

python_s3: ./protos/s3_grpc.proto
	python3 -m grpc_tools.protoc --python_out=python/s3 --grpc_python_out=python/s3 --pyi_out=python/s3 -I ./protos ./protos/s3_grpc.proto

python_imgrot: ./protos/image_rotate.proto
	python3 -m grpc_tools.protoc --python_out=python/image_rotate --grpc_python_out=python/image_rotate --pyi_out=python/image_rotate -I ./protos ./protos/image_rotate.proto