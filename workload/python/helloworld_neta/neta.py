import os
import socket
import struct

import logging
log = logging.getLogger(__name__)
log.setLevel(logging.INFO)


class S3Neta:
    def __init__(self, cid: int, port: int):
        self.VSOCK_CID = cid
        self.VSOCK_PORT = port
        
        self._aws_access_key_id  = os.environ.get('AWS_ACCESS_KEY')
        self._aws_secret_access_key = os.environ.get('AWS_SECRET_ACCESS_KEY')
        self._aws_region = os.environ.get('AWS_REGION')

    def get_object(self, bucket, key):
        self.sock = socket.socket(socket.AF_VSOCK, socket.SOCK_STREAM)
        self.sock.connect((self.VSOCK_CID, self.VSOCK_PORT))
        
        payload = S3Request(
            access_key=self._aws_access_key_id,
            secret_access_key=self._aws_secret_access_key,
            region=self._aws_region,
            operation="GET",
            bucket_name=bucket,
            object_name=key
        )
        payload = payload.serialize()
        self.sock.sendall(payload)
        
        # Receive response
        offsets, data = self.get_response()
        response = data[offsets[0]:offsets[1]].decode()
        
        if response == "success":
            print("S3 GET operation successful")
            payload = data[offsets[1]:] 
            return payload
        elif response == "error":
            print("S3 operation failed")
            return None
        else:
            print("Unknown response")
            return None
    
    def put_object(self, bucket, key, data):
        self.sock = socket.socket(socket.AF_VSOCK, socket.SOCK_STREAM)
        self.sock.connect((self.VSOCK_CID, self.VSOCK_PORT))
        
        payload = S3Request(
            access_key=self._aws_access_key_id,
            secret_access_key=self._aws_secret_access_key,
            region=self._aws_region,
            operation="PUT",
            bucket_name=bucket,
            object_name=key,
            payload=data
        )
        payload = payload.serialize()
        self.sock.sendall(payload)
        
        # Receive response
        offsets, data = self.get_response()
        response = data[offsets[0]:].decode()
        
        if response == "success":
            print("S3 PUT operation successful")
            return response
        elif response == "error":
            print("S3 operation failed: {payload.decode()}")
            return None
        else:
            print("Unknown response: {response.decode()}")
            return None
    
    def get_response(self):
        # Receive response
        data = self.sock.recv(4)
        if not data:
            print("Failed to receive data")
            return None
        data_length = struct.unpack(">I", data)[0]
        print(f"Data length: {data_length}")
        
        data = self.sock.recv(data_length)
        print(f"Actual data length: {len(data)}")
        n_entires = struct.unpack(">I", data[:4])[0]
        print(f"Number of entries: {n_entires}")
        
        offsets = []
        for n in range (0, n_entires):
            offset = struct.unpack(">I", data[4*n + 4 : 4*n + 8])[0]
            offsets.append(offset)
        
        return offsets, data
        


class S3Request:
    def __init__(self, access_key, secret_access_key, region, operation, bucket_name, object_name, payload=None):
        self.access_key = access_key
        self.secret_access_key = secret_access_key
        self.region = region
        self.operation = operation
        self.bucket_name = bucket_name
        self.object_name = object_name
        self.payload = payload

    def serialize(self):
        # Encode strings to UTF-8 bytes
        access_key_bytes = self.access_key.encode('utf-8')
        secret_access_key_bytes = self.secret_access_key.encode('utf-8')
        region_bytes = self.region.encode('utf-8')
        operation_bytes = self.operation.encode('utf-8')
        bucket_name_bytes = self.bucket_name.encode('utf-8')
        object_name_bytes = self.object_name.encode('utf-8')
        
        if self.payload:
            payload_bytes = self.payload
            
            access_key_offset = 32
            secret_access_key_offset = access_key_offset + len(access_key_bytes)
            region_offset = secret_access_key_offset + len(secret_access_key_bytes)
            operation_offset = region_offset + len(region_bytes)
            bucket_name_offset = operation_offset + len(operation_bytes)
            object_name_offset = bucket_name_offset + len(bucket_name_bytes)
            payload_offset = object_name_offset + len(object_name_bytes)
            
            total_length = (payload_offset + len(payload_bytes))

            # Pack length offset
            length_offset = struct.pack(">IIIIIIIII", 
                                        total_length, 
                                        7,  # number of entries
                                        access_key_offset,
                                        secret_access_key_offset,
                                        region_offset,
                                        operation_offset,
                                        bucket_name_offset,
                                        object_name_offset,
                                        payload_offset)
        
        else:
            access_key_offset = 28
            secret_access_key_offset = access_key_offset + len(access_key_bytes)
            region_offset = secret_access_key_offset + len(secret_access_key_bytes)
            operation_offset = region_offset + len(region_bytes)
            bucket_name_offset = operation_offset + len(operation_bytes)
            object_name_offset = bucket_name_offset + len(bucket_name_bytes)
            
            total_length = (object_name_offset + len(object_name_bytes))

            # Pack length offset
            length_offset = struct.pack(">IIIIIIII", 
                                        total_length, 
                                        6,  # number of entries
                                        access_key_offset,
                                        secret_access_key_offset,
                                        region_offset,
                                        operation_offset,
                                        bucket_name_offset,
                                        object_name_offset)
        
        # Combine all parts
        return (length_offset + 
                access_key_bytes + secret_access_key_bytes + region_bytes +
                operation_bytes + bucket_name_bytes + object_name_bytes)