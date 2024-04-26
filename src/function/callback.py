import os
from enum import Enum, auto
from typing import Any, cast, TypedDict

from shared.clients.sqs_client import SqsClient
from shared.logger import logger


class Operation(Enum):
  push = auto()
  pop = auto()


# Attributes in the payload
class PushAttributes(TypedDict):
  CallbackId: str
  CallbackNumber: str


class PopAttributes(TypedDict):
  pass


class InvocationParameters(TypedDict):
  LambdaOperation: str


# Contact flow payload structure
class ContactData(TypedDict):
  Attributes: PushAttributes | PopAttributes


class Details(TypedDict):
  ContactData: ContactData
  Parameters: InvocationParameters


class CallbackEvent(TypedDict):
  Details: Details


# Return values
class PopReturn(TypedDict):
  CallbackNumber: str


class PushReturn(TypedDict):
  pass


def handler(event: CallbackEvent, _context: Any) -> PushReturn | PopReturn:
  sqs_client = SqsClient[PushAttributes](os.environ["SQS_QUEUE_URL"])

  operation = event["Details"]["Parameters"]["LambdaOperation"]
  attributes = event["Details"]["ContactData"]["Attributes"]

  if Operation[operation] == Operation.push:
    push_attributes = cast(PushAttributes, attributes)
    logger.info(f"Pushing callback with id={push_attributes['CallbackId']}")
    sqs_client.push(push_attributes)
    return PushReturn()
  elif Operation[operation] == Operation.pop:
    callback = sqs_client.pop()
    logger.info(f"Popping callback with id={callback['CallbackId']}")
    return callback
  else:
    raise Exception(f"Unexpected operation: {operation}")
