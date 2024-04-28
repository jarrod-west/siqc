import dotenv
from mypy_boto3_cloudformation.type_defs import ParameterTypeDef
from mypy_boto3_connect.type_defs import (
  InstanceSummaryTypeDef,
  ListPhoneNumbersSummaryTypeDef,
)
from pathlib import Path
from typing import cast, TypedDict

FLOW_CONTENT_DIRECTORY = Path("../cloudformation/flow_content")
FLOW_EXPORT_DIRECTORY = Path("../output/flow_content")

FLOW_NAMES = {
  "inbound": "CallbackInbound",
  "outbound": "CallbackOutbound",
  "agent_whisper": "CallbackAgentWhisper",
  "outbound_whisper": "CallbackOutboundWhisper",
}
ROUTING_PROFILE_NAME = "Callback Routing Profile"


class Parameters(TypedDict):
  """System parameters provided in the .env file."""

  InstanceAlias: str
  PrivateNumber: str
  PublicNumber: str
  AgentUsername: str
  CustomerNumber: str
  CallerId: str
  DefaultRoutingProfile: str


class DeployKwArgs(TypedDict):
  """Arguments for the cloudformation deploy."""

  StackName: str
  TemplateBody: str
  Parameters: list[ParameterTypeDef]


class StackConfig:
  """General stack configuration."""

  stack_name: str
  stack_template_file: str

  def __init__(self, stack_name: str, stack_template_file: str) -> None:
    """Constructor.

    Args:
        stack_name (str): The name of the stack
        stack_template_file (str): The location of the stack's template file
    """
    self.stack_name = stack_name
    self.stack_template_file = stack_template_file


class InstanceConfig:
  """Configuration details of the Connect instance."""

  instance: InstanceSummaryTypeDef
  private_number: ListPhoneNumbersSummaryTypeDef
  public_number: ListPhoneNumbersSummaryTypeDef

  def __init__(
    self,
    instance: InstanceSummaryTypeDef,
    private_number: ListPhoneNumbersSummaryTypeDef,
    public_number: ListPhoneNumbersSummaryTypeDef,
  ) -> None:
    """Constructor.

    Args:
        instance (InstanceSummaryTypeDef): The summary of the instance
        private_number (ListPhoneNumbersSummaryTypeDef): The summary of the private phone number
        public_number (ListPhoneNumbersSummaryTypeDef): The summary of the public phone number
    """
    self.instance = instance
    self.private_number = private_number
    self.public_number = public_number


# Stack config

MAIN_STACK_CONFIG = StackConfig("sicq-main-stack", "../cloudformation/main.yaml")
CALLBACK_FLOW_STACK_CONFIG = StackConfig(
  "sicq-callback-flow-stack", "../cloudformation/callback_flows.yaml"
)
WHISPER_FLOW_STACK_CONFIG = StackConfig(
  "sicq-whisper-flow-stack", "../cloudformation/whisper_flows.yaml"
)


def read_parameters() -> Parameters:
  """Load parameters from the .env file.

  Returns:
      Parameters: The loaded parameters
  """
  return cast(Parameters, dotenv.dotenv_values())


def create_logical_id(name: str) -> str:
  """Creates a valid cloudformation logical id from a string.

  Args:
      name (str): The name, in general format

  Returns:
      str: The valid cloudformation logical id
  """
  # Create a valid cloudformation logical ID by removing "word-delimiters" and forcing upper camel case
  delims = " -_"

  logical_id = name

  for delim in delims:
    logical_id = "".join(
      [token[0].upper() + token[1:] for token in logical_id.split(delim)]
    )

  return logical_id
