from os import environ
from typing import Any, TypedDict


class DialledNumber(TypedDict):
  CallbackNumber: str


def handler(_event: Any, _context: Any) -> DialledNumber:
  return {
    "CallbackNumber": environ["OUTBOUND_NUMBER"]
  }