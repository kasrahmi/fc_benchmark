import time
import boto3
import os
import argparse


def download_file(outdir, bucket, object_name, s3_client):
    response = s3_client.download_file(bucket, object_name, outdir)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--outdir', type=str, required=True, help='Output directory and name')
    parser.add_argument('--bucket', type=str, required=True, help='Bucket name')
    parser.add_argument('--object', type=str, required=True, help='File name')
    args = parser.parse_args()
    
    object_name = os.path.basename(args.outdir)
    
    for i in range(3):
        s3_client = boto3.client('s3')
        download_file(args.outdir, args.bucket, object_name, s3_client)
    
    time.sleep(60)
    s3_client = boto3.client('s3')
    download_file(args.outdir, args.bucket, object_name, s3_client)