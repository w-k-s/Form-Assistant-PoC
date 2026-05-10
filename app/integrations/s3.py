import boto3
from app.config import settings


class S3Storage:
    def __init__(self):
        self._client = boto3.client(
            "s3",
            region_name=settings.aws_region,
        )

    def upload(self, source_path: str, destination_bucket: str, key: str) -> None:
        self._client.upload_file(source_path, destination_bucket, key)

    def generate_presigned_url(
        self, destination_bucket: str, key: str, expires_in: int = 3600
    ) -> str:
        return self._client.generate_presigned_url(
            "get_object",
            Params={"Bucket": destination_bucket, "Key": key},
            ExpiresIn=expires_in,
        )
