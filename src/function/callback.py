from enum import Enum, auto
from os import environ

# from pynamodb.models import Model
# from pynamodb.attributes import UnicodeAttribute, UTCDateTimeAttribute, DiscriminatorAttribute
from typing import Any, cast, TypedDict

from src.shared.clients.sqs_client import SqsClient


class Operation(Enum):
  push = auto()
  pop = auto()


class PushAttributes(TypedDict):
  CallbackId: str
  CallbackNumber: str


class PopAttributes(TypedDict):
  pass


class CallbackEvent(TypedDict):
  LambdaOperation: str
  Attributes: PushAttributes | PopAttributes


# Return values
class PopReturn(TypedDict):
  CallbackNumber: str


class PushReturn(TypedDict):
  pass


# Database model
# class CallbackModel(Model):
#   class Meta:
#     table_name = environ["TABLE_NAME"]
#   callback_id = UnicodeAttribute(hash_key=True)
#   callback_number = UnicodeAttribute()
#   callback_time = UTCDateTimeAttribute()


def handler(event: CallbackEvent, _context: Any) -> PushReturn | PopReturn:
  sqs_client = SqsClient[PushAttributes](environ["SQS_QUEUE_URL"])

  if Operation[event["LambdaOperation"]] == Operation.push:
    attributes = cast(PushAttributes, event["Attributes"])
    sqs_client.push(attributes)
    return {}
  elif Operation[event["LambdaOperation"]] == Operation.pop:
    return cast(PopReturn, sqs_client.pop())
  else:
    raise Exception(f"Unexpected operation: {event['LambdaOperation']}")
