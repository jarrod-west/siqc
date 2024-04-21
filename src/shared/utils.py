from dotenv import dotenv_values
from mypy_boto3_cloudformation.type_defs import ParameterTypeDef
from mypy_boto3_connect.type_defs import (
  InstanceSummaryTypeDef,
  ListPhoneNumbersSummaryTypeDef,
)
from pathlib import Path
from typing import cast, TypedDict

FLOW_CONTENT_DIRECTORY = Path("./cloudformation/flow_content")
FLOW_EXPORT_DIRECTORY = Path("output/flow_content")

FLOW_NAMES = {"inbound": "CallbackInbound", "outbound": "CallbackOutbound"}
ROUTING_PROFILE_NAME = "Callback Routing Profile"


class Parameters(TypedDict):  # TODO: Separate file?
  InstanceAlias: str
  PrivateNumber: str
  PublicNumber: str
  AgentUsername: str
  DefaultRoutingProfile: str


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
  private_number: ListPhoneNumbersSummaryTypeDef
  public_number: ListPhoneNumbersSummaryTypeDef

  def __init__(
    self,
    instance: InstanceSummaryTypeDef,
    private_number: ListPhoneNumbersSummaryTypeDef,
    public_number: ListPhoneNumbersSummaryTypeDef,
  ) -> None:
    self.instance = instance
    self.private_number = private_number
    self.public_number = public_number


# Stack config
MAIN_STACK_CONFIG = StackConfig("sicq-main-stack", "./cloudformation/main.yaml")
FLOW_STACK_CONFIG = StackConfig("sicq-flow-stack", "./cloudformation/flows.yaml")


def read_parameters() -> Parameters:
  return cast(Parameters, dotenv_values())


def create_logical_id(name: str) -> str:
  # Create a valid cloudformation logical ID by removing "word-delimiters" and forcing upper camel case
  delims = " -_"

  logical_id = name

  for delim in delims:
    logical_id = "".join(
      [token[0].upper() + token[1:] for token in logical_id.split(delim)]
    )

  return logical_id
