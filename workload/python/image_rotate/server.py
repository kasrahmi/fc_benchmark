from concurrent import futures
import os
import argparse
import grpc
import helloworld_pb2
import helloworld_pb2_grpc

import boto3
from PIL import Image, ImageOps, ImageFilter
import io

BUCKET_NAME = "kasrahmi-benchmark"
ROTATE = 1

def image_rotate_function(image_bytes):
    try:
        img = Image.open(io.BytesIO(image_bytes))
        for i in range(ROTATE):
            img = img.filter(ImageFilter.BLUR)
            img = img.filter(ImageFilter.MinFilter)
            img = img.filter(ImageFilter.EDGE_ENHANCE_MORE)
            img = img.filter(ImageFilter.SHARPEN)
            img = img.transpose(Image.ROTATE_90)

        # Save the image in memory instead of the filesystem
        img_byte_arr = io.BytesIO()
        img.save(img_byte_arr, format='PNG')
        return img_byte_arr.getvalue()
    except Exception as e:
        return f"python.image_rotate.ImageNotFound.Error:{e}".encode()

def upload_file(object_name, bucket, s3_client, payload):
    response = s3_client.put_object(Bucket=bucket, Key=object_name, Body=payload)
    return "success"

def download_file(object_name, bucket, s3_client):
    response = s3_client.get_object(Bucket=bucket, Key=object_name)
    return response['Body'].read()

class Greeter(helloworld_pb2_grpc.GreeterServicer):
    def SayHello(self, request, context):
        filename = request.name
        print(f"Processing image: {filename}")
        s3_client = boto3.client('s3')

        # Download image from S3
        image_bytes = download_file(filename, BUCKET_NAME, s3_client)

        # Rotate image
        rotated_image_bytes = image_rotate_function(image_bytes)

        # Generate a new filename for the rotated image
        new_filename = f"{os.path.splitext(filename)[0]}_rotated.png"

        # Upload the rotated image back to S3
        upload_file(new_filename, BUCKET_NAME, s3_client, rotated_image_bytes)

        msg = f"fn: ImageRotate | image: {filename} | rotated_image: {new_filename} | runtime: Python"
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
    parser.add_argument('-a', '--addr', type=str, default="172.16.0.2", help='Server IP address')
    parser.add_argument('-p', '--port', type=str, default="50051", help='Server port number')
    args = parser.parse_args()

    serve(args.addr, args.port)
