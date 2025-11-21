import boto3
from pathlib import Path


def download_file(bucket: str, key: str, local_path: str) -> None:
    s3 = boto3.client("s3", endpoint_url="http://localhost:9000",
                      aws_access_key_id="admin",
                      aws_secret_access_key="admin123")

    Path(local_path).parent.mkdir(parents=True, exist_ok=True)
    s3.download_file(bucket, key, local_path)
