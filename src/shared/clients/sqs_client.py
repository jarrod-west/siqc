import json
from mypy_boto3_sqs.client import (
  SQSClient as AwsSqsClient,
)
from typing import cast, Generic, TypeVar

from shared.clients.aws_client import AwsClient

MessageType = TypeVar("MessageType")


class SqsClient(AwsClient, Generic[MessageType]):
  client: AwsSqsClient

  def __init__(self, queue_url: str) -> None:
    super().__init__("sqs")
    self.queue_url = queue_url

  def push(self, payload: MessageType) -> None:
    self.client.send_message(
      QueueUrl=self.queue_url,
      MessageBody=json.dumps(payload),
      MessageGroupId="callbacks",
    )

  def pop(self) -> MessageType:
    response = self.client.receive_message(
      QueueUrl=self.queue_url, MaxNumberOfMessages=1
    )
    message = response["Messages"][0]
    self.client.delete_message(
      QueueUrl=self.queue_url, ReceiptHandle=message["ReceiptHandle"]
    )
    return cast(MessageType, json.loads(message["Body"]))
