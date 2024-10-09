from concurrent import futures
import os
import argparse
import grpc
import helloworld_pb2
import helloworld_pb2_grpc
import boto3

BUCKET_NAME = "jyp-benchmark"
INPUT_FILE = "money.txt"
OUTPUT_FILE = "output_money.txt"

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
    try:
        s3_client.upload_file(file_dir, bucket, object_name)
        print(f"Successfully uploaded {object_name} to {bucket}.")
        return True
    except Exception as e:
        print(f"Error uploading {object_name} to S3: {e}")
        return False

class Greeter(helloworld_pb2_grpc.GreeterServicer):
    def SayHello(self, request, context):
        filename = request.name
        input_file_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "../../temp", INPUT_FILE)
        output_file_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "../../temp", OUTPUT_FILE)
        s3_client = boto3.client('s3')

        # Download the input file from S3
        if not download_file(input_file_path, INPUT_FILE, BUCKET_NAME, s3_client):
            return helloworld_pb2.HelloReply(message="Error: Unable to download input file.")

        try:
            # Open the input file, subtract 100 from the number, and save it to the output file
            with open(input_file_path, "r") as f:
                number = int(f.read().strip())
                result = number - 100
            
            with open(output_file_path, "w") as f:
                f.write(str(result))
            
            print(f"Processed input: {number}, result: {result}")

            # Upload the output file to S3
            if not upload_file(output_file_path, OUTPUT_FILE, BUCKET_NAME, s3_client):
                return helloworld_pb2.HelloReply(message="Error: Unable to upload output file.")

            msg = f"Processed file: {filename} | Input: {number} | Result: {result}"
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
    parser = argparse.ArgumentParser(description='gRPC client for web_serve')
    parser.add_argument('-a', '--addr', type=str, default="localhost", help='Server IP address')
    parser.add_argument('-p', '--port', type=str, default="50051", help='Server port number')
    args = parser.parse_args()

    serve(args.addr, args.port)
