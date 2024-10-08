from concurrent import futures
import grpc
import argparse
import random
import string
import pyaes
import boto3
from io import BytesIO
import helloworld_pb2
import helloworld_pb2_grpc

# Constants
BUCKET_NAME = "kasrahmi-benchmark"  # Your S3 bucket name
KEY = b'\xa1\xf6%\x8c\x87}_\xcd\x89dHE8\xbf\xc9,'  # AES key

# Helper function to generate a random string
def generate(length):
    letters = string.ascii_lowercase + string.digits
    return ''.join(random.choice(letters) for i in range(length))

# S3 helper functions (in-memory download/upload)
def download_file(object_name, bucket, s3_client):
    try:
        response = s3_client.get_object(Bucket=bucket, Key=object_name)
        return response['Body'].read()
    except Exception as e:
        print(f"Error downloading {object_name} from S3: {e}")
        return None

def upload_file(object_name, bucket, s3_client, payload):
    try:
        s3_client.put_object(Bucket=bucket, Key=object_name, Body=payload)
        print(f"Successfully uploaded {object_name} to {bucket}.")
        return True
    except Exception as e:
        print(f"Error uploading {object_name} to S3: {e}")
        return False

class Greeter(helloworld_pb2_grpc.GreeterServicer):
    def SayHello(self, request, context):
        # AES encryption setup
        aes = pyaes.AESModeOfOperationCTR(KEY)
        
        # S3 client setup
        s3_client = boto3.client('s3')

        input_filename = request.name
        output_filename = f"{input_filename.split('.')[0]}_encrypted.txt"

        # Download the file from S3 (directly into memory)
        input_data = download_file(input_filename, BUCKET_NAME, s3_client)
        if input_data is None:
            return helloworld_pb2.HelloReply(message="Error: Unable to download input file from S3")

        try:
            # Encrypt the content in memory
            ciphertext = aes.encrypt(input_data.decode('utf-8'))

            # Upload the encrypted content back to S3 (from memory)
            if not upload_file(output_filename, BUCKET_NAME, s3_client, ciphertext):
                return helloworld_pb2.HelloReply(message="Error: Unable to upload encrypted file to S3")

            msg = f"File {input_filename} encrypted and saved as {output_filename}"

        except Exception as e:
            msg = f"Error processing file: {e}"

        return helloworld_pb2.HelloReply(message=msg)

# gRPC server setup
def serve(addr, port):
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=1))
    helloworld_pb2_grpc.add_GreeterServicer_to_server(Greeter(), server)
    server.add_insecure_port(f"{addr}:{port}")
    server.start()
    print(f"Server started, listening on {port}")
    server.wait_for_termination()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='gRPC server for AES encryption with S3 integration')
    parser.add_argument('-a', '--addr', type=str, default="localhost", help='Server IP address')
    parser.add_argument('-p', '--port', type=str, default="50051", help='Server port number')
    args = parser.parse_args()

    serve(args.addr, args.port)
