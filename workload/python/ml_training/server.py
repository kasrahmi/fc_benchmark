import os
import argparse
import grpc
import helloworld_pb2
import helloworld_pb2_grpc
import boto3
import joblib
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from concurrent import futures

BUCKET_NAME = "jyp-benchmark"

def upload_file(file_dir, object_name, bucket, s3_client):
    try:
        s3_client.upload_file(file_dir, bucket, object_name)
        print(f"File {object_name} uploaded to {bucket}")
    except Exception as e:
        print(f"Error uploading file: {e}")

def download_file(file_dir, object_name, bucket, s3_client):
    try:
        s3_client.download_file(bucket, object_name, file_dir)
        print(f"File {object_name} downloaded from {bucket}")
    except Exception as e:
        print(f"Error downloading file: {e}")

def train_model(data_file, model_filename):
    # Load the training data (assuming it's in CSV format)
    data = pd.read_csv(data_file)  # Adjust as needed based on your data format
    X = data.drop('target', axis=1)  # Replace 'target' with your actual target column name
    y = data['target']  # Adjust based on your dataset

    # Train a model (Random Forest as an example)
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    model = RandomForestClassifier()
    model.fit(X_train, y_train)

    # Save the model to a file
    joblib.dump(model, model_filename)

class Greeter(helloworld_pb2_grpc.GreeterServicer):
    def SayHello(self, request, context):
        filename = request.name
        file_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "../../temp", filename)
        model_filename = f"{filename}_model.joblib"

        os.makedirs(os.path.dirname(file_dir), exist_ok=True)  # Ensure the temp directory exists
        s3_client = boto3.client('s3')

        # Download training data from S3
        download_file(file_dir, filename, BUCKET_NAME, s3_client)

        # Train the model
        train_model(file_dir, model_filename)

        # Upload the trained model back to S3
        upload_file(model_filename, model_filename, BUCKET_NAME, s3_client)

        msg = f"Model training complete. Model uploaded as {model_filename}."
        return helloworld_pb2.HelloReply(message=msg)

def serve(addr, port):
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=1))
    helloworld_pb2_grpc.add_GreeterServicer_to_server(Greeter(), server)
    server.add_insecure_port(f"{addr}:{port}")
    server.start()
    print(f"Server started, listening on {port}")
    server.wait_for_termination()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='gRPC ML training server')
    parser.add_argument('-a', '--addr', type=str, default="192.168.0.2", help='Server IP address')
    parser.add_argument('-p', '--port', type=str, default="50051", help='Server port number')
    args = parser.parse_args()

    serve(args.addr, args.port)
