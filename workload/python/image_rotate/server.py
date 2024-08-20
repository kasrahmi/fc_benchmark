import logging
import boto3
from botocore.exceptions import ClientError
import os
import argparse

import grpc
from concurrent import futures 

import image_rotate_pb2
import image_rotate_pb2_grpc
from PIL import Image, ImageOps, ImageFilter


parser = argparse.ArgumentParser()
parser.add_argument("-b", "--bucket", type=str, default="jyp-benchmark", help='Bucket name')
parser.add_argument("-a", "--addr", dest="addr", default="0.0.0.0", help="IP address")
parser.add_argument("-p", "--port", dest="port", default="50051", help="serve port")
parser.add_argument("-r", "--rotate", type=int, default="1", help="times to rotate")
args = parser.parse_args()

BUCKET_NAME = args.bucket
ROTATE = args.rotate

def image_rotate_function(load_image_path, save_image_path):
    try:
        img = Image.open(load_image_path)
        for i in range(ROTATE):
            img = img.filter(ImageFilter.BLUR)
            img = img.filter(ImageFilter.MinFilter)
            img = img.filter(ImageFilter.EDGE_ENHANCE_MORE)
            img = img.filter(ImageFilter.SHARPEN)
            img = img.transpose(Image.ROTATE_90)
        img.save(save_image_path)
        return f"python.image_rotate.{load_image_path}"
    except Exception as e:
        return f"python.image_rotate.ImageNotFound.Error:{e}"


def upload_file(file_dir, object_name, bucket):
    # Upload the file
    s3_client = boto3.client('s3')
    try:
        response = s3_client.upload_file(file_dir, bucket, object_name)
    except ClientError as e:
        logging.error(e)
        return False
    return True


def download_file(file_dir, object_name, bucket):
    # Downloadload the file
    s3_client = boto3.client('s3')
    try:
        response = s3_client.download_file(bucket, object_name, file_dir)
    except ClientError as e:
        logging.error(e)
        return False
    return True


def save_image_path(image_path):
    directory, filename = os.path.split(image_path)
    name, extension = os.path.splitext(filename)
    new_filename = f"{name}_rotated{extension}"
    save_image_path = os.path.join(directory, new_filename)
    
    return save_image_path, new_filename


class ImageRotate(image_rotate_pb2_grpc.ImageRotateServicer):
    def RotateImage(self, request, context):
        filename = request.name
        file_dir = os.path.join("temp", filename)
        save_dir, save_name = save_image_path(file_dir)
        print(f"filedir: {file_dir}")
        
        # Download file from S3
        download_file(file_dir, filename, BUCKET_NAME)
        
        # Rotate Image
        response = image_rotate_function(file_dir, save_dir)
        
        # Upload Image
        upload_file(save_dir, save_name, BUCKET_NAME)
        
        msg = f"fn: ImageRotate | image: {filename} | return msg: {response} | runtime: Python"
        return image_rotate_pb2.GetRotatedImage(message=msg)

def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=1))
    image_rotate_pb2_grpc.add_ImageRotateServicer_to_server(ImageRotate(), server)
    address = (args.addr + ":" + args.port)
    server.add_insecure_port(address)
    print("Start ImageRotate-python server. Addr: " + address)
    server.start()
    server.wait_for_termination()

if __name__ == '__main__':
    serve()
