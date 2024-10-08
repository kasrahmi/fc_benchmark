from concurrent import futures
import os
import argparse
import grpc
import helloworld_pb2
import helloworld_pb2_grpc

import boto3
import numpy as np
from sklearn.linear_model import LogisticRegression
import time
import pandas as pd

BUCKET_NAME = "jyp-benchmark"
TRAINING_FILE = "training_data.csv"  # Name of the dataset in the S3 bucket

# Function to generate synthetic data
def generate_synthetic_data(num_samples=10000, num_features=100):
    X = np.random.rand(num_samples, num_features)  # Features
    y = np.random.randint(2, size=num_samples)     # Labels
    return X, y

# Function to load real data from a CSV file
def load_data_from_csv(file_dir):
    data = pd.read_csv(file_dir)
    X = data.iloc[:, :-1].values  # All columns except the last one as features
    y = data.iloc[:, -1].values   # The last column as labels
    return X, y

# Training function
def train_model(X, y):
    model = LogisticRegression()
    start_time = time.time()
    model.fit(X, y)
    end_time = time.time()
    return model, end_time - start_time

# AWS S3 file download
def download_file(file_dir, object_name, bucket, s3_client):
    try:
        s3_client.download_file(bucket, object_name, file_dir)
        print(f"Successfully downloaded {object_name} from {bucket}.")
        return True
    except Exception as e:
        print(f"Error downloading {object_name} from S3: {e}")
        return False

# AWS S3 file upload
def upload_file(file_dir, object_name, bucket, s3_client):
    response = s3_client.upload_file(file_dir, bucket, object_name)

class Greeter(helloworld_pb2_grpc.GreeterServicer):
    def SayHello(self, request, context):
        filename = request.name
        file_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "../../temp", filename)
        s3_client = boto3.client('s3')

        # Try to download the dataset from S3
        if download_file(file_dir, TRAINING_FILE, BUCKET_NAME, s3_client):
            # Load real data from CSV
            X, y = load_data_from_csv(file_dir)
            print(f"Training on real data from S3: {TRAINING_FILE}")
        else:
            # Fallback to synthetic data
            print("Falling back to synthetic data.")
            X, y = generate_synthetic_data()

        # Train the model
        model, train_time = train_model(X, y)

        # (Optional) Upload the trained model to S3 if needed, or log the training time
        msg = f"Model trained in {train_time:.4f} seconds using {'real' if os.path.exists(file_dir) else 'synthetic'} data!"

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
    parser = argparse.ArgumentParser(description='gRPC client for ml_training')
    parser.add_argument('-a', '--addr', type=str, default="localhost", help='Server IP address')
    parser.add_argument('-p', '--port', type=str, default="50051", help='Server port number')
    args = parser.parse_args()

    serve(args.addr, args.port)
