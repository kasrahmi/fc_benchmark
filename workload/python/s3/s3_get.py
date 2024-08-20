import logging
import boto3
from botocore.exceptions import ClientError
import os
import argparse


def download_file(outdir, bucket, object_name=None):
    """Download a file to an S3 bucket

    :param outdir: path+filename to download
    :param bucket: Bucket to upload to
    :param object_name: S3 object name. If not specified then file_name is used
    :return: True if file was uploaded, else False
    """

    # If S3 object_name was not specified, use file_name
    if object_name is None:
        object_name = os.path.basename(outdir)

    # Upload the file
    s3_client = boto3.client('s3')
    try:
        response = s3_client.download_file(bucket, object_name, outdir)
    except ClientError as e:
        logging.error(e)
        return False
    return True

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--outdir', type=str, required=True, help='Output directory and name')
    parser.add_argument('--bucket', type=str, required=True, help='Bucket name')
    parser.add_argument('--object', type=str, help='File name')
    args = parser.parse_args()
    
    download_file(args.outdir, args.bucket, args.object)
    