from concurrent import futures
import grpc
import argparse
import boto3
from io import BytesIO
import helloworld_pb2
import helloworld_pb2_grpc

BUCKET_NAME = "kasrahmi-benchmark"

# AWS S3 file upload (directly from memory)
def upload_file(object_name, bucket, s3_client, payload):
    try:
        s3_client.put_object(Bucket=bucket, Key=object_name, Body=payload)
        print(f"Successfully uploaded {object_name} to {bucket}.")
        return "success"
    except Exception as e:
        return f"Error uploading {object_name} to S3: {e}"

# AWS S3 file download (directly into memory)
def download_file(object_name, bucket, s3_client):
    try:
        response = s3_client.get_object(Bucket=bucket, Key=object_name)
        return response['Body'].read()
    except Exception as e:
        print(f"Error downloading {object_name} from S3: {e}")
        return None

class Greeter(helloworld_pb2_grpc.GreeterServicer):
    def SayHello(self, request, context):
        input_filename = request.name
        output_filename = f"{input_filename.split('.')[0]}_result.txt"
        
        s3_client = boto3.client('s3')

        # Download input file from S3 (into memory)
        input_data = download_file(input_filename, BUCKET_NAME, s3_client)
        if input_data is None:
            return helloworld_pb2.HelloReply(message="Error: Unable to download input file.")

        try:
            # Process the input: subtract 100 from the number
            number = float(input_data.decode('utf-8').strip())
            result = number - 100
            result_data = str(result).encode('utf-8')

            print(f"Processed input: {number}, result: {result}")

            # Upload result file to S3 (directly from memory)
            if upload_file(output_filename, BUCKET_NAME, s3_client, result_data) != "success":
                return helloworld_pb2.HelloReply(message="Error: Unable to upload output file.")

            msg = f"Processed file: {input_filename} | Input: {number} | Result: {result} | Output saved as: {output_filename}"
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
    parser = argparse.ArgumentParser(description='gRPC server for processing numbers')
    parser.add_argument('--addr', type=str, default="localhost", help='Server IP address')
    parser.add_argument('--port', type=str, default="50051", help='Server port number')
    args = parser.parse_args()

    serve(args.addr, args.port)
