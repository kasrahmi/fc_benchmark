import socket

def vsock_server():
    VSOCK_PORT = 50051

    # Create a vsock socket
    sock = socket.socket(socket.AF_VSOCK, socket.SOCK_STREAM)
    
    # Bind to all interfaces (CID_ANY) on the specified port
    sock.bind((socket.VMADDR_CID_ANY, VSOCK_PORT))
    
    sock.listen(1)
    print(f"Server listening on port {VSOCK_PORT}")

    while True:
        conn, (cid, port) = sock.accept()
        print(f"Connection from CID: {cid}, Port: {port}")

        # Receive data from the client
        data = conn.recv(1024).decode()
        print(f"Received: {data}")

        # Send a response
        response = f"Hello from guest! You said: {data}"
        conn.send(response.encode())

        conn.close()

if __name__ == "__main__":
    vsock_server()