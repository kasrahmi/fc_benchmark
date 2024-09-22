from concurrent import futures

from sklearn.feature_extraction.text import TfidfVectorizer
#from sklearn.externals import joblib
import joblib

import pandas as pd
import os
import re

import argparse
import grpc
import helloworld_pb2
import helloworld_pb2_grpc


cleanup_re = re.compile('[^a-z]+')

def cleanup(sentence):
    sentence = sentence.lower()
    sentence = cleanup_re.sub(' ', sentence).strip()
    return sentence

dataset = pd.read_csv(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'dataset.csv'))
#dataset = pd.read_csv('/var/local/dir/dataset.csv')
df_input = pd.DataFrame()
dataset['train'] = dataset['Text'].apply(cleanup)
tfidf_vect = TfidfVectorizer(min_df=100).fit(dataset['train'])
x = 'The ambiance is magical. The food and service was nice! The lobster and cheese was to die for and our steaks were cooked perfectly.  '
df_input['x'] = [x]
df_input['x'] = df_input['x'].apply(cleanup)
X = tfidf_vect.transform(df_input['x'])

model = joblib.load(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'lr_model.pk'))
print('Model is ready')

class Greeter(helloworld_pb2_grpc.GreeterServicer):
    def SayHello(self, request, context):
        msg = 'Hello, %s!' % request.name
        y = model.predict(X)
        
        msg = "Hello, %s!" % request.name
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