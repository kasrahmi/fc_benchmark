import argparse
import grpc
import helloworld_pb2
import helloworld_pb2_grpc

def run(addr, port, name):
    print("Will try to greet world ...")
    with grpc.insecure_channel(f"{addr}:{port}") as channel:
        stub = helloworld_pb2_grpc.GreeterStub(channel)
        response = stub.SayHello(helloworld_pb2.HelloRequest(name=name))
    print("Greeter client received: " + response.message)

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='gRPC client')
    parser.add_argument('-a', '--addr', type=str, default="192.168.0.2", help='Server IP address')
    parser.add_argument('-p', '--port', type=str, default="50051", help='Server port number')
    parser.add_argument('-n', '--name', type=str, default="you", help='Name of the image file to rotate')
    
    args = parser.parse_args()
    
    run(args.addr, args.port, args.name)