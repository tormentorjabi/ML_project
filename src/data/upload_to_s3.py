import boto3


def upload_file(bucket: str, key: str, local_path: str) -> None:
    s3 = boto3.client("s3", endpoint_url="http://localhost:9000",
                      aws_access_key_id="admin",
                      aws_secret_access_key="admin123")
    s3.upload_file(local_path, bucket, key)
