from concurrent import futures
import grpc
import helloworld_pb2
import helloworld_pb2_grpc
import boto3
import os
from flask import Flask, send_file
from io import BytesIO
import argparse

BUCKET_NAME = "jyp-benchmark"  # Replace with your S3 bucket name

app = Flask(__name__)
s3_client = boto3.client('s3')

# Function to download file from S3
def download_file_from_s3(object_name):
    try:
        response = s3_client.get_object(Bucket=BUCKET_NAME, Key=object_name)
        file_data = response['Body'].read()
        print(f"Successfully downloaded {object_name} from S3.")
        return BytesIO(file_data)  # Return as BytesIO for in-memory operations
    except Exception as e:
        print(f"Error downloading {object_name} from S3: {e}")
        return None

# Flask route to serve files
@app.route('/serve/<filename>')
def serve_file(filename):
    file_data = download_file_from_s3(filename)
    if file_data:
        return send_file(file_data, mimetype='application/octet-stream', as_attachment=True, download_name=filename)
    else:
        return f"File {filename} not found in S3."

# gRPC service
class Greeter(helloworld_pb2_grpc.GreeterServicer):
    def SayHello(self, request, context):
        filename = request.name  # Get filename from the gRPC request
        file_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "../../temp", filename)

        # Download file from S3
        file_data = download_file_from_s3(filename)

        # If file exists in S3, serve it
        if file_data:
            print(f"File {filename} served from S3!")
            msg = f"File {filename} downloaded and served from S3."
        else:
            print(f"File {filename} not found!")
            msg = f"File {filename} not found in S3."

        return helloworld_pb2.HelloReply(message=msg)

# gRPC server setup
def serve(addr, port):
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=1))
    helloworld_pb2_grpc.add_GreeterServicer_to_server(Greeter(), server)
    server.add_insecure_port(f"{addr}:{port}")
    server.start()
    print(f"gRPC server started on {addr}:{port}")
    server.wait_for_termination()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='gRPC server for web_serve with S3')
    parser.add_argument('-a', '--addr', type=str, default="localhost", help='Server IP address')
    parser.add_argument('-p', '--port', type=str, default="50051", help='Server port number')
    args = parser.parse_args()

    # Start gRPC server
    serve(args.addr, args.port)
