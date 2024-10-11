from concurrent import futures
import os
import argparse
import grpc
import helloworld_pb2
import helloworld_pb2_grpc
import random
import string
import pyaes
import boto3

# Constants
BUCKET_NAME = "kasrahmi-benchmark"  # Your S3 bucket name
KEY = b'\xa1\xf6%\x8c\x87}_\xcd\x89dHE8\xbf\xc9,'  # AES key

# Helper function to generate a random string
def generate(length):
    letters = string.ascii_lowercase + string.digits
    return ''.join(random.choice(letters) for i in range(length))

# S3 helper functions
def download_file(file_dir, object_name, bucket, s3_client):
    try:
        s3_client.download_file(bucket, object_name, file_dir)
        print(f"Successfully downloaded {object_name} from {bucket}.")
        return True
    except Exception as e:
        print(f"Error downloading {object_name} from S3: {e}")
        return False

def upload_file(file_dir, object_name, bucket, s3_client):
    try:
        s3_client.upload_file(file_dir, bucket, object_name)
        print(f"Successfully uploaded {object_name} to {bucket}.")
        return True
    except Exception as e:
        print(f"Error uploading {object_name} to S3: {e}")
        return False

class Greeter(helloworld_pb2_grpc.GreeterServicer):
    def SayHello(self, request, context):
        # AES encryption setup
        aes = pyaes.AESModeOfOperationCTR(KEY)
        
        # File paths for input and output
        input_filename = request.name
        input_file_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "../../temp", input_filename)
        output_filename = os.path.splitext(input_filename)[0] + "_encrypted.txt"
        output_file_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "../../temp", output_filename)

        # S3 client setup
        s3_client = boto3.client('s3')

        # Download the file from S3
        if not download_file(input_file_path, input_filename, BUCKET_NAME, s3_client):
            return helloworld_pb2.HelloReply(message="Error: Unable to download input file from S3")

        # Read and encrypt the content of the file
        try:
            with open(input_file_path, 'r') as f:
                message = f.read()

            # Encrypt the message
            ciphertext = aes.encrypt(message)

            # Save the encrypted content to the output file
            with open(output_file_path, 'wb') as f:
                f.write(ciphertext)

            # Upload the encrypted file to S3
            if not upload_file(output_file_path, output_filename, BUCKET_NAME, s3_client):
                return helloworld_pb2.HelloReply(message="Error: Unable to upload output file to S3")

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
