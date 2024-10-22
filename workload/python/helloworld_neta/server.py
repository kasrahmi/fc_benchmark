from concurrent import futures
import os

import argparse
import grpc
import helloworld_pb2
import helloworld_pb2_grpc

from neta import S3Neta


class Greeter(helloworld_pb2_grpc.GreeterServicer):
    def SayHello(self, request, context):
        neta = S3Neta(2, 52)
        buf = neta.get_object("jyp-benchmark", "img_small.jpg")
        print(f"{len(buf)} bytes received")
        
        temp = neta.put_object("jyp-benchmark", "temp_img_small.jpg", buf)
        print(f"Operation result: {temp}")
        
        msg = f"fn: ImageRotate | image: img_small.jpg | return msg: temp_img_small.jpg | runtime: Python"
        return helloworld_pb2.HelloReply(message=msg)


def serve(addr, port):
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=1))
    helloworld_pb2_grpc.add_GreeterServicer_to_server(Greeter(), server)
    server.add_insecure_port(f"{addr}:{port}")
    server.start()
    print("Server started, listening on " + port)
    server.wait_for_termination()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='gRPC client for image rotation')
    parser.add_argument('-a', '--addr', type=str, default="192.168.0.2", help='Server IP address')
    parser.add_argument('-p', '--port', type=str, default="50051", help='Server port number')
    args = parser.parse_args()
    
    serve(args.addr, args.port)