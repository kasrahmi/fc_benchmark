from concurrent import futures
import argparse
import grpc
import helloworld_pb2
import helloworld_pb2_grpc
import boto3
import pickle
import torch
import rnn
import io
import string
import psutil
import os

# S3 setup
BUCKET_NAME = "kasrahmi-benchmark"
S3_PARAMS_FILE = "rnn_params.pkl"
S3_MODEL_FILE = "rnn_model.pth"
S3_INPUT_FILE = "in.txt"
S3_OUTPUT_FILE = "out.txt"

s3_client = boto3.client('s3')

# Download file from S3
def download_file_from_s3(s3_client, bucket, object_name, file_path):
    try:
        s3_client.download_file(bucket, object_name, file_path)
        print(f"Downloaded {object_name} from {bucket}")
        return True
    except Exception as e:
        print(f"Error downloading file from S3: {e}")
        return False

# Upload file to S3
def upload_file_to_s3(file_path, bucket, object_name, s3_client):
    try:
        s3_client.upload_file(file_path, bucket, object_name)
        print(f"Uploaded {object_name} to {bucket}")
    except Exception as e:
        print(f"Error uploading file to S3: {e}")

# Memory usage
def get_memory_usage():
    pid = os.getpid()
    python_process = psutil.Process(pid)
    return python_process.memory_info()[0] / 2.0**20  # in MB

# Load RNN model
def load_rnn_model():
    with open(S3_PARAMS_FILE, "wb") as f:
        s3_client.download_fileobj(BUCKET_NAME, S3_PARAMS_FILE, f)
    with open(S3_PARAMS_FILE, "rb") as f:
        params = pickle.load(f)
    
    all_categories = ['French', 'Czech', 'Dutch', 'Polish', 'Scottish', 'Chinese', 'English', 'Italian',
                      'Portuguese', 'Japanese', 'German', 'Russian', 'Korean', 'Arabic', 'Greek', 
                      'Vietnamese', 'Spanish', 'Irish']
    n_categories = len(all_categories)
    all_letters = string.ascii_letters + " .,;'-"
    n_letters = len(all_letters) + 1

    rnn_model = rnn.RNN(n_letters, 128, n_letters, all_categories, n_categories, all_letters, n_letters)

    # Load model state
    with open(S3_MODEL_FILE, "wb") as f:
        s3_client.download_fileobj(BUCKET_NAME, S3_MODEL_FILE, f)
    with open(S3_MODEL_FILE, "rb") as f:
        buffer = io.BytesIO(f.read())
        rnn_model.load_state_dict(torch.load(buffer, weights_only=True))
    rnn_model.eval()
    
    return rnn_model, all_categories, all_letters

# Server gRPC logic
class Greeter(helloworld_pb2_grpc.GreeterServicer):
    def SayHello(self, request, context):
        # Track memory usage
        memory_before = get_memory_usage()
        
        # Download input file
        if download_file_from_s3(s3_client, BUCKET_NAME, S3_INPUT_FILE, S3_INPUT_FILE):
            with open(S3_INPUT_FILE, 'r') as f:
                language = f.readline().strip()
                start_letters = f.readline().strip()

            # Load model and parameters
            rnn_model, all_categories, all_letters = load_rnn_model()
            output_names = list(rnn_model.samples(language, start_letters))

            # Save output to S3
            value = str(output_names)
            with open(S3_OUTPUT_FILE, 'w') as f:
                f.write(value)
            upload_file_to_s3(S3_OUTPUT_FILE, BUCKET_NAME, S3_OUTPUT_FILE, s3_client)

            memory_after = get_memory_usage()
            return helloworld_pb2.HelloReply(message=f"Prediction completed. Memory used: {memory_after - memory_before:.4f} MB")
        else:
            return helloworld_pb2.HelloReply(message="Error downloading input file from S3")

def serve(addr, port):
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=1))
    helloworld_pb2_grpc.add_GreeterServicer_to_server(Greeter(), server)
    server.add_insecure_port(f"{addr}:{port}")
    server.start()
    print(f"Server started, listening on {addr}:{port}")
    server.wait_for_termination()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='gRPC RNN Server')
    parser.add_argument('-a', '--addr', type=str, default="localhost", help='Server IP address')
    parser.add_argument('-p', '--port', type=str, default="50051", help='Server port number')
    args = parser.parse_args()

    serve(args.addr, args.port)
