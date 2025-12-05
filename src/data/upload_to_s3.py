import os

import boto3


def upload_file(bucket: str, key: str, local_path: str) -> None:
    endpoint = os.getenv("S3_ENDPOINT_URL", "http://localhost:9000")
    access_key = os.getenv("S3_ACCESS_KEY", "admin")
    secret_key = os.getenv("S3_SECRET_KEY", "admin123")

    s3 = boto3.client(
        "s3",
        endpoint_url=endpoint,
        aws_access_key_id=access_key,
        aws_secret_access_key=secret_key,
    )
    s3.upload_file(local_path, bucket, key)
