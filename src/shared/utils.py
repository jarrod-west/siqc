from dotenv import dotenv_values
from mypy_boto3_cloudformation.type_defs import ParameterTypeDef
from mypy_boto3_connect.type_defs import (
  InstanceSummaryTypeDef,
  PhoneNumberSummaryTypeDef,
)
from pathlib import Path
from typing import cast, TypedDict

FLOW_CONTENT_DIRECTORY = Path("./cloudformation/flow_content")


class Parameters(TypedDict):  # TODO: Separate file?
  InstanceAlias: str
  PrivateNumber: str
  PublicNumber: str


class DeployKwArgs(TypedDict):
  StackName: str
  TemplateBody: str
  Parameters: list[ParameterTypeDef]


class StackConfig:
  stack_name: str
  stack_template_file: str

  def __init__(self, stack_name: str, stack_template_file: str) -> None:
    self.stack_name = stack_name
    self.stack_template_file = stack_template_file


class InstanceConfig:
  instance: InstanceSummaryTypeDef
  private_number: PhoneNumberSummaryTypeDef
  public_number: PhoneNumberSummaryTypeDef

  def __init__(
    self,
    instance: InstanceSummaryTypeDef,
    private_number: PhoneNumberSummaryTypeDef,
    public_number: PhoneNumberSummaryTypeDef,
  ) -> None:
    self.instance = instance
    self.private_number = private_number
    self.public_number = public_number


MAIN_STACK_CONFIG = StackConfig("sicq-main-stack", "./cloudformation/main.yaml")
FLOW_STACK_CONFIG = StackConfig("sicq-flow-stack", "./cloudformation/flows.yaml")


def read_parameters() -> Parameters:
  return cast(Parameters, dotenv_values())
