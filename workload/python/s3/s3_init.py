import time
import boto3



if __name__ == "__main__":
    for i in range(3):
        s3_client = boto3.client('s3')

    time.sleep(30)
    s3_client = boto3.client('s3')
