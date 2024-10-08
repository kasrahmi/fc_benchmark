from concurrent import futures
import os
import argparse
import grpc
import helloworld_pb2
import helloworld_pb2_grpc

import boto3
from PIL import Image
from io import BytesIO

BUCKET_NAME = "kasrahmi-benchmark"  # Update with the correct bucket name

# Image resizing function, handling image in memory
def image_resize_function(image_data, size=(128, 128)):
    try:
        img = Image.open(BytesIO(image_data))
        img_resized = img.resize(size, Image.Resampling.LANCZOS)
        
        img_byte_arr = BytesIO()
        img_resized.save(img_byte_arr, format=img.format)
        return img_byte_arr.getvalue()
    except Exception as e:
        return f"python.image_resize.ImageNotFound.Error:{e}".encode()

# Upload file to S3 directly from memory
def upload_file(object_name, bucket, s3_client, payload):
    s3_client.put_object(Bucket=bucket, Key=object_name, Body=payload)

# Download file from S3 directly into memory
def download_file(object_name, bucket, s3_client):
    response = s3_client.get_object(Bucket=bucket, Key=object_name)
    return response['Body'].read()

class Greeter(helloworld_pb2_grpc.GreeterServicer):
    def SayHello(self, request, context):
        filename = request.name
        s3_client = boto3.client('s3')

        # Download image from S3
        image_data = download_file(filename, BUCKET_NAME, s3_client)
        
        # Resize the image
        resized_image_data = image_resize_function(image_data, size=(200, 200))  # Example size

        # Upload the resized image back to S3
        resized_filename = f"{os.path.splitext(filename)[0]}_resized{os.path.splitext(filename)[1]}"
        upload_file(resized_filename, BUCKET_NAME, s3_client, resized_image_data)

        msg = f"fn: ImageResize | image: {filename} resized and uploaded as {resized_filename} | runtime: Python"
        return helloworld_pb2.HelloReply(message=msg)

def serve(addr, port):
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=1))
    helloworld_pb2_grpc.add_GreeterServicer_to_server(Greeter(), server)
    server.add_insecure_port(f"{addr}:{port}")
    server.start()
    print(f"Server started, listening on {port}")
    server.wait_for_termination()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='gRPC server for image resizing')
    parser.add_argument('-a', '--addr', type=str, default="192.168.0.2", help='Server IP address')
    parser.add_argument('-p', '--port', type=str, default="50051", help='Server port number')
    args = parser.parse_args()

    serve(args.addr, args.port)
