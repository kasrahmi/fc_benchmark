from concurrent import futures
import os

import argparse
import grpc
import helloworld_pb2
import helloworld_pb2_grpc

import boto3
from PIL import Image, ImageOps, ImageFilter

def image_resize_function(load_image_path, save_image_path, size=(128,128)):
    try:
        img = Image.open(load_image_path)
        
        img_resized = img.resize((200, 200), Image.Resampling.LANCZOS)  # Example size (200, 200)
        img_resized.save(save_image_path)
        
    except Exception as e:
        return f"python.image_resize.ImageNotFound.Error:{e}"

BUCKET_NAME = "jyp-benchmark"

def upload_file(file_dir, object_name, bucket, s3_client):
    response = s3_client.upload_file(file_dir, bucket, object_name)


def download_file(file_dir, object_name, bucket, s3_client):
    response = s3_client.download_file(bucket, object_name, file_dir)

def save_image_path(image_path):
    directory, filename = os.path.split(image_path)
    name, extension = os.path.splitext(filename)
    new_filename = f"{name}{extension}"
    save_image_path = os.path.join(directory, new_filename)

    return save_image_path, new_filename

class Greeter(helloworld_pb2_grpc.GreeterServicer):
    def SayHello(self, request, context):
        filename = request.name
        file_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "../../temp", filename)
        save_dir, save_name = save_image_path(file_dir)
        print(f"filedir: {file_dir}")
        s3_client = boto3.client('s3')
        
        # Download file from S3
        download_file(file_dir, filename, BUCKET_NAME, s3_client)
        
        # Resize Image
        response = image_resize_function(file_dir, save_dir)
        
        # Upload Image
        upload_file(save_dir, save_name, BUCKET_NAME, s3_client)
        
        msg = f"fn: ImageResize | image: {filename} | return msg: {response} | runtime: Python"
        return helloworld_pb2.HelloReply(message=msg)


def serve(addr, port):
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=1))
    helloworld_pb2_grpc.add_GreeterServicer_to_server(Greeter(), server)
    server.add_insecure_port(f"{addr}:{port}")
    server.start()
    print("Server started, listening on " + port)
    server.wait_for_termination()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='gRPC client for image resizing')
    parser.add_argument('-a', '--addr', type=str, default="192.168.0.2", help='Server IP address')
    parser.add_argument('-p', '--port', type=str, default="50051", help='Server port number')
    args = parser.parse_args()
    
    serve(args.addr, args.port)
