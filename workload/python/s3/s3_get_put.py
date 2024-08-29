import time
import boto3
from botocore.exceptions import ClientError
import os
import argparse

def download_file(outdir, bucket, object_name, s3_client):
    response = s3_client.download_file(bucket, object_name, outdir)

def upload_file(file_name, bucket, object_name, s3_client):
    response = s3_client.upload_file(file_name, bucket, object_name)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--outdir', type=str, required=True, help='Output directory and name')
    parser.add_argument('--filename', type=str, required=True, help='File name')
    parser.add_argument('--bucket', type=str, required=True, help='Bucket name')
    parser.add_argument('--object', type=str, required=True, help='Object name')
    args = parser.parse_args()

    object_name = os.path.basename(args.filename)
    s3_client = boto3.client('s3')
    
    for i in range(3):
        upload_file(args.filename, args.bucket, object_name, s3_client)
        download_file(args.outdir, args.bucket, object_name, s3_client)
    
    time.sleep(60)
    upload_file(args.filename, args.bucket, object_name, s3_client)
    download_file(args.outdir, args.bucket, object_name, s3_client)