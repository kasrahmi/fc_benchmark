from concurrent import futures
import os

import argparse
import grpc
import helloworld_pb2
import helloworld_pb2_grpc

import boto3
from PIL import Image, ImageOps, ImageFilter


BUCKET_NAME = "jyp-benchmark"


def upload_file(object_name, bucket, s3_client, payload):
    response = s3_client.put_object(Bucket=bucket, Key=object_name, Body=payload)
    return "success"


def download_file(object_name, bucket, s3_client):
    response = s3_client.get_object(Bucket=bucket, Key=object_name)
    return response.get('Body').read()


class Greeter(helloworld_pb2_grpc.GreeterServicer):
    def SayHello(self, request, context):
        filename = request.name
        s3_client = boto3.client('s3')
        
        # Download file from S3
        response = download_file(filename, BUCKET_NAME, s3_client)
        
        # Rotate Image
        
        # Upload Image
        response = upload_file(f"temp_{filename}", BUCKET_NAME, s3_client, response)
        
        msg = f"fn: ImageRotate | image: {filename} | return msg: {response} | runtime: Python"
        return helloworld_pb2.HelloReply(message=msg)


def serve(addr, port):
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=1))
    helloworld_pb2_grpc.add_GreeterServicer_to_server(Greeter(), server)
    server.add_insecure_port(f"{addr}:{port}")
    server.start()
    print("Server started, listening on " + port)
    server.wait_for_termination()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='gRPC client for image rotation')
    parser.add_argument('-a', '--addr', type=str, default="192.168.0.2", help='Server IP address')
    parser.add_argument('-p', '--port', type=str, default="50051", help='Server port number')
    args = parser.parse_args()
    
    serve(args.addr, args.port)