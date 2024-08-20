import argparse
import grpc
import image_rotate_pb2
import image_rotate_pb2_grpc

def run(addr, port, name):
    channel = grpc.insecure_channel(f'{addr}:{port}')
    stub = image_rotate_pb2_grpc.ImageRotateStub(channel)
    
    request = image_rotate_pb2.SendImage(name=name)
    response = stub.RotateImage(request)
    
    print(f"Server response: {response.message}")

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='gRPC client for image rotation')
    parser.add_argument('-a', '--addr', type=str, default="172.16.0.2", help='Server IP address')
    parser.add_argument('-p', '--port', type=int, default="50051", help='Server port number')
    parser.add_argument('-n', '--name', type=str, default="img_medium.jpg", help='Name of the image file to rotate')
    
    args = parser.parse_args()
    
    run(args.addr, args.port, args.name)