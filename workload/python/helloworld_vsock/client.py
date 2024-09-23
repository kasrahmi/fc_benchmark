import socket
import os

def vsock_client():
    VSOCK_PATH = "./v.sock"  # Path to the Firecracker vsock file
    GUEST_CID = 3  # CID of the guest, as configured in Firecracker
    VSOCK_PORT = 50051  # Port the server is listening on

    # Create a Unix domain socket
    sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
    
    # Connect to the Firecracker vsock
    sock.connect(VSOCK_PATH)

    # Send the CONNECT command to establish the vsock connection
    sock.sendall(f"CONNECT {VSOCK_PORT}\n".encode())

    # Wait for the OK response
    data = sock.recv(1024).decode().strip()
    if data.startswith("OK"):
        print("vsock connection established")
        
        # Now we can communicate
        message = "Hello from host!"
        sock.sendall(message.encode())
        
        response = sock.recv(1024).decode()
        print(f"Received from guest: {response}")

    sock.close()

if __name__ == "__main__":
    vsock_client()