from dotenv import dotenv_values
from mypy_boto3_connect.type_defs import InstanceSummaryTypeDef, PhoneNumberSummaryTypeDef
from typing import TypedDict

class Parameters(TypedDict): # TODO: Separate file?
  InstanceAlias: str
  PrivateNumber: str
  PublicNumber: str

class StackConfig(TypedDict):
  stack_name: str
  stack_template_file: str

class StackConfig:
  def __init__(self, stack_name: str, stack_template_file: str) -> None:
    self.stack_name = stack_name
    self.stack_template_file = stack_template_file

class InstanceConfig:
  def __init__(self, instance: InstanceSummaryTypeDef, private_number: PhoneNumberSummaryTypeDef, public_number: PhoneNumberSummaryTypeDef) -> None:
    self.instance = instance
    self.private_number = private_number
    self.public_number = public_number

MAIN_STACK_CONFIG = StackConfig("sicq-main-stack", "./cloudformation/main.yaml")

def read_parameters() -> Parameters:
  return dotenv_values()
