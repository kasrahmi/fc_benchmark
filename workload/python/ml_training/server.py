from concurrent import futures
import argparse
import grpc
import psutil
import os
import pickle
import re
import pandas as pd
from io import BytesIO
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
import boto3  # AWS SDK for Python (Boto3)

# gRPC import for benchmark service
import helloworld_pb2
import helloworld_pb2_grpc

# Initialize AWS S3 client
s3_client = boto3.client('s3')  # specify your region
bucket_name = "kasrahmi-benchmark"  # replace with your actual S3 bucket name

# Memory tracking setup
pid = os.getpid()
python_process = psutil.Process(pid)
memory_use_old = 0

# Text cleanup regex
cleanup_re = re.compile('[^a-z]+')

def cleanup(sentence):
    """Clean up text data for processing."""
    sentence = sentence.lower()
    sentence = cleanup_re.sub(' ', sentence).strip()
    return sentence

def log_memory_usage(stage, file_append):
    """Log memory usage after a specific stage."""
    global memory_use_old
    memory_use = python_process.memory_info()[0] / 2**20  # in MB
    print(f'memory use {stage}: {memory_use - memory_use_old}', file=file_append)
    memory_use_old = memory_use

def download_file(object_name, bucket, s3_client):
    """Download file from AWS S3 directly into memory."""
    response = s3_client.get_object(Bucket=bucket, Key=object_name)
    return response.get('Body').read()

def upload_file(object_name, bucket, s3_client, payload):
    """Upload in-memory file data to AWS S3."""
    response = s3_client.put_object(Bucket=bucket, Key=object_name, Body=payload)
    return "success"

class Greeter(helloworld_pb2_grpc.GreeterServicer):
    def SayHello(self, request, context):
        """Run the benchmark processing within the SayHello method."""
        file_append = open("../funcs.txt", "a")
        # Step 1: Log initial memory usage
        log_memory_usage("initial", file_append)

        # Step 2: Download and process dataset
        file_name = request.name
        csv_data = download_file(file_name, bucket_name, s3_client)
        data = BytesIO(csv_data)
        df = pd.read_csv(data)
        df['train'] = df['Text'].apply(cleanup)
        # Step 3: Log memory after data load
        log_memory_usage("after data load", file_append)

        # Step 4: Train logistic regression model
        model = LogisticRegression(max_iter=100)
        tfidf_vectorizer = TfidfVectorizer(min_df=1000).fit(df['train'])
        train_data = tfidf_vectorizer.transform(df['train'])
        model.fit(train_data, df['Score'])

        # Step 5: Serialize and upload model to S3
        model_buffer = BytesIO()
        pickle.dump(model, model_buffer)
        model_buffer.seek(0)
        upload_file("finalized_model.sav", bucket_name, s3_client, model_buffer.getvalue())

        # Step 6: Log memory after training and upload
        log_memory_usage("after model training and upload", file_append)
        file_append.close()

        # Return gRPC response
        msg = f"Hello, {request.name}! Benchmark completed successfully."
        return helloworld_pb2.HelloReply(message=msg)

def serve(addr, port):
    """Run gRPC server."""
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=1))
    helloworld_pb2_grpc.add_GreeterServicer_to_server(Greeter(), server)
    server.add_insecure_port(f"{addr}:{port}")
    server.start()
    print(f"Server started, listening on {addr}:{port}")
    server.wait_for_termination()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='gRPC server for benchmark processing')
    parser.add_argument('-a', '--addr', type=str, default="0.0.0.0", help='Server IP address')
    parser.add_argument('-p', '--port', type=str, default="50051", help='Server port number')
    args = parser.parse_args()
    
    serve(args.addr, args.port)

