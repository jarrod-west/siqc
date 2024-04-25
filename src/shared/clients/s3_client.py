from mypy_boto3_s3.client import S3Client as AwsS3Client

from shared.clients.aws_client import AwsClient
from shared.logger import logger


class S3Client(AwsClient):
  client: AwsS3Client

  def __init__(self) -> None:
    super().__init__("s3")

  def upload_file(self, filename: str, bucket_name: str, path: str) -> None:
    logger.info(f"Starting upload of {filename}...")

    self.client.upload_file(Filename=filename, Bucket=bucket_name, Key=path)

    logger.info(f"Upload of {filename} complete")
