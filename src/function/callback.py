import os
from enum import Enum, auto
from typing import Any, cast, TypedDict

from shared.clients.sqs_client import SqsClient


class Operation(Enum):
  push = auto()
  pop = auto()


# Attributes in the payload
class PushAttributes(TypedDict):
  LambdaOperation: str
  CallbackId: str
  CallbackNumber: str


class PopAttributes(TypedDict):
  LambdaOperation: str


# Contact flow payload structure
class ContactData(TypedDict):
  Attributes: PushAttributes | PopAttributes


class Details(TypedDict):
  ContactData: ContactData


class CallbackEvent(TypedDict):
  Details: Details


# Return values
class PopReturn(TypedDict):
  CallbackNumber: str


class PushReturn(TypedDict):
  pass


def handler(event: CallbackEvent, _context: Any) -> PushReturn | PopReturn:
  sqs_client = SqsClient[PushAttributes](os.environ["SQS_QUEUE_URL"])

  attributes = event["Details"]["ContactData"]["Attributes"]

  if Operation[attributes["LambdaOperation"]] == Operation.push:
    push_attributes = cast(PushAttributes, attributes)
    sqs_client.push(push_attributes)
    return {}
  elif Operation[attributes["LambdaOperation"]] == Operation.pop:
    return cast(PopReturn, sqs_client.pop())
  else:
    raise Exception(f"Unexpected operation: {attributes['LambdaOperation']}")
