import socket
import ctypes
import time

def start_server(host='192.168.0.2', port=50051):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind((host, port))
        s.listen()
        print(f'Server listening on {host}:{port}')

        while True:
            conn, addr = s.accept()
            with conn:
                print(f'Connected by {addr}')
                while True:
                    data = conn.recv(1024)
                    if not data:
                        break
                    name = data.decode('utf-8')
                    msg = f'hello, {name}'
                    conn.sendall(msg.encode('utf-8'))

if __name__ == "__main__":
    start_server()

