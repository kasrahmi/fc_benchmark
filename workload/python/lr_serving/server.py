from concurrent import futures
import os
import argparse
import grpc
import helloworld_pb2
import helloworld_pb2_grpc

import boto3
import joblib  # To load the pre-trained model
import numpy as np
import pandas as pd

BUCKET_NAME = "jyp-benchmark"
MODEL_FILE = "trained_model.pkl"  # Model name stored in S3

# Function to generate synthetic data for inference
def generate_synthetic_data(num_samples=1, num_features=100):
    X = np.random.rand(num_samples, num_features)  # Random input data
    return X

# AWS S3 file download
def download_file(file_dir, object_name, bucket, s3_client):
    try:
        s3_client.download_file(bucket, object_name, file_dir)
        print(f"Successfully downloaded {object_name} from {bucket}.")
        return True
    except Exception as e:
        print(f"Error downloading {object_name} from S3: {e}")
        return False

# Function to load the model from a file
def load_model(file_dir):
    model = joblib.load(file_dir)
    return model

class Greeter(helloworld_pb2_grpc.GreeterServicer):
    def SayHello(self, request, context):
        filename = request.name  # Placeholder for input filename (if any)
        file_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "../../temp", filename)
        s3_client = boto3.client('s3')

        # Download the pre-trained model from S3
        model_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "trained_model.pkl")
        if download_file(model_path, MODEL_FILE, BUCKET_NAME, s3_client):
            print("Model successfully downloaded from S3.")
        else:
            return helloworld_pb2.HelloReply(message="Failed to download model from S3!")

        # Load the model
        model = load_model(model_path)

        # Generate synthetic data for inference
        X = generate_synthetic_data()

        # Perform inference
        predictions = model.predict(X)
        print(f"Predictions: {predictions}")

        msg = f"Model served. Predictions: {predictions.tolist()}"
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
    parser = argparse.ArgumentParser(description='gRPC server for lr_serving')
    parser.add_argument('-a', '--addr', type=str, default="localhost", help='Server IP address')
    parser.add_argument('-p', '--port', type=str, default="50051", help='Server port number')
    args = parser.parse_args()

    serve(args.addr, args.port)
