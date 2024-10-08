from concurrent import futures
import os
import argparse
import grpc
import helloworld_pb2
import helloworld_pb2_grpc

import boto3
import cv2
import io

BUCKET_NAME = "kasrahmi-benchmark"

def video_processing_function(video_bytes):
    try:
        # Create a VideoCapture object from the byte stream
        video_file = io.BytesIO(video_bytes)
        video = cv2.VideoCapture(video_file)

        width = int(video.get(3))
        height = int(video.get(4))
        fourcc = cv2.VideoWriter_fourcc(*'MPEG')
        out = cv2.VideoWriter('output.avi', fourcc, 20.0, (width, height))

        while video.isOpened():
            ret, frame = video.read()
            if ret:
                gray_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                out.write(gray_frame)
            else:
                break

        video.release()
        out.release()

        # Save processed video in memory instead of the filesystem
        with open('output.avi', "rb") as f:
            processed_video_bytes = f.read()
        
        return processed_video_bytes
    except Exception as e:
        return f"python.video_processing.VideoProcessingError:{e}".encode()

def upload_file(object_name, bucket, s3_client, payload):
    response = s3_client.put_object(Bucket=bucket, Key=object_name, Body=payload)
    return "success"

def download_file(object_name, bucket, s3_client):
    response = s3_client.get_object(Bucket=bucket, Key=object_name)
    return response['Body'].read()

class Greeter(helloworld_pb2_grpc.GreeterServicer):
    def SayHello(self, request, context):
        filename = request.name
        print(f"Processing video: {filename}")
        s3_client = boto3.client('s3')

        # Download video from S3
        video_bytes = download_file(filename, BUCKET_NAME, s3_client)

        # Process video
        processed_video_bytes = video_processing_function(video_bytes)

        # Generate a new filename for the processed video
        new_filename = f"{os.path.splitext(filename)[0]}_processed.avi"

        # Upload the processed video back to S3
        upload_file(new_filename, BUCKET_NAME, s3_client, processed_video_bytes)

        msg = f"fn: VideoProcessing | video: {filename} | processed_video: {new_filename} | runtime: Python"
        return helloworld_pb2.HelloReply(message=msg)

def serve(addr, port):
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=1))
    helloworld_pb2_grpc.add_GreeterServicer_to_server(Greeter(), server)
    server.add_insecure_port(f"{addr}:{port}")
    server.start()
    print("Server started, listening on " + port)
    server.wait_for_termination()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='gRPC client for video processing')
    parser.add_argument('-a', '--addr', type=str, default="192.168.0.2", help='Server IP address')
    parser.add_argument('-p', '--port', type=str, default="50051", help='Server port number')
    args = parser.parse_args()

    serve(args.addr, args.port)
