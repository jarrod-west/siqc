from contextlib import contextmanager
from typing import Any, Callable
from mypy_boto3_cloudformation.type_defs import (
  ParameterTypeDef,
  ValidateTemplateOutputTypeDef,
)
from mypy_boto3_connect.type_defs import (
  InstanceSummaryTypeDef,
  ListPhoneNumbersSummaryTypeDef,
  ContactFlowTypeDef,
  ContactFlowSummaryTypeDef,
  StartOutboundVoiceContactResponseTypeDef,
)

from shared.utils import StackConfig


@contextmanager
def not_raises() -> Any:
  """Helper context to explicitly check function doesn't raise an error.

  Raises:
      AssertionError: Thrown when any error occurs within the context

  Returns:
      Any: The context
  """
  try:
    yield
  except Exception as error:
    raise AssertionError(f"An unexpected exception {error} raised.")


class MockCloudformationClient:
  """Mocks a cloudformation client."""

  def __init__(self, assert_parameters: bool = True) -> None:
    """Constructor."""
    self.calls = ["__init__"]
    self.assert_parameters = assert_parameters

  def validate(self, template: str) -> ValidateTemplateOutputTypeDef:
    """Validate a cloudformation template, which also parses the parameters.

    Args:
        template (str): The cloudformation template.

    Returns:
        ValidateTemplateOutputTypeDef: The stack validation object, including parameters
    """
    if self.assert_parameters:
      assert template == "template body"
    self.calls.append("validate")
    return {
      "Parameters": [
        {"ParameterKey": "InstanceArn"},
        {"ParameterKey": "PrivateNumberArn"},
        {"ParameterKey": "PublicNumberArn"},
        {"ParameterKey": "CallbackInboundContent"},
      ],
      "Description": "A mock validation response",
      "Capabilities": [],
      "CapabilitiesReason": "reason",
      "DeclaredTransforms": [],
      "ResponseMetadata": {
        "RequestId": "request",
        "HTTPStatusCode": 200,
        "HTTPHeaders": {},
        "RetryAttempts": 0,
      },
    }

  def deploy_stack(
    self, stack_config: StackConfig, template: str, parameters: list[ParameterTypeDef]
  ) -> None:
    """Deploy a stack from a cloudformation template with the provided parameters.

    Args:
        stack_config (StackConfig): General stack configuration
        template (str): The cloudformation template
        parameters (list[ParameterTypeDef]): Parameters for the stack

    Raises:
        ex: botocore.client.ClientError other than "No updates are to be performed"
    """
    if self.assert_parameters:
      assert stack_config.stack_name == "stack1"
      assert stack_config.stack_template_file == "template location 1"
      assert template == "template body"
      assert parameters[:-1] == [
        {"ParameterKey": "InstanceArn", "ParameterValue": "instance arn"},
        {"ParameterKey": "PrivateNumberArn", "ParameterValue": "private arn"},
        {"ParameterKey": "PublicNumberArn", "ParameterValue": "public arn"},
      ]
      assert parameters[-1]["ParameterKey"] == "CallbackInboundContent"
      assert parameters[-1]["ParameterValue"].startswith('{\n  "Version":')
    self.calls.append("deploy_stack")

  def get_stack_resource_mapping(self, stack_name: str) -> dict[str, str]:
    """Retrieve a mapping of a stack's resources by logical name to ARN.

    Args:
        stack_name (str): The name of the stack

    Returns:
        dict[str, str]: A mapping of resources by logical name to ARN.
    """
    if self.assert_parameters:
      assert stack_name == "stack1"
    self.calls.append("get_stack_resource_mapping")
    return {"new resource 1": "new arn1", "new resource 2": "new arn2"}

  def _get_summary(
    self,
    list_function: str,
    top_level_key: str,
    match_key: str,
    match_values: str | list[str],
    filter_predicate: Callable[[Any], bool] = lambda x: True,
    paginate_args: dict[str, str | int] = {},
  ) -> Any:
    assert False


class MockConnectClient:
  """Mocks a connect client."""

  def __init__(self, instance_alias: str) -> None:
    """Constuctor.

    Args:
        instance_alias (str): The alias of the relevant Connect instance
    """
    assert instance_alias == "alias"
    self.calls = ["__init__"]
    self.instance: InstanceSummaryTypeDef = {
      "Id": "instance id",
      "Arn": "instance arn",
      "InstanceAlias": "alias",
    }

  def unassign_contact_flow_number(self, phone_number: str) -> None:
    """Remove a phone number from a contact flow.

    Args:
        phone_number (str): The phone number in E.164 format
    """
    assert phone_number == "private"
    self.calls.append("unassign_contact_flow_number")

  def assign_user_to_routing_profile(
    self, username: str, routing_profile_name: str
  ) -> None:
    """Assign a Connect user to a routing profile.

    Args:
        username (str): The username of the user
        routing_profile_name (str): The name of the routing profile
    """
    assert username == "agent"
    assert routing_profile_name in ["routing", "Callback Routing Profile"]
    self.calls.append("assign_user_to_routing_profile")

  def assign_contact_flow_number(self, flow_name: str, phone_number: str) -> None:
    """Assign a phone number to a contact flow.

    Args:
        flow_name (str): The name of the contact flow
        phone_number (str): The phone number in E.164 format
    """
    assert flow_name == "CallbackInbound"
    assert phone_number == "private"
    self.calls.append("assign_contact_flow_number")

  def get_phone_number_summaries(
    self, phone_numbers: list[str]
  ) -> list[ListPhoneNumbersSummaryTypeDef]:
    """Retrieve the summaries of instance phone numbers matching the given values.

    Args:
        phone_numbers (list[str]): A list of phone numbers in E.164 format

    Returns:
        list[ListPhoneNumbersSummaryTypeDef]: The summaries of the matching phone numbers
    """
    assert phone_numbers == ["private", "public"]
    self.calls.append("get_phone_number_summaries")

    return [
      {
        "PhoneNumber": "number 1",
        "PhoneNumberArn": "private arn",
      },
      {
        "PhoneNumber": "number 2",
        "PhoneNumberArn": "public arn",
      },
    ]

  def get_flow_summaries(
    self, flow_names: list[str]
  ) -> list[ContactFlowSummaryTypeDef]:
    """Retrieve the summaries of instance contact flows matching the given names.

    Args:
        flow_names (list[str]): A list of contact flow names

    Returns:
        list[ContactFlowSummaryTypeDef]: The summaries of the contact flows
    """
    assert flow_names == [
      "CallbackInbound",
      "CallbackOutbound",
      "CallbackAgentWhisper",
      "CallbackOutboundWhisper",
    ]
    self.calls.append("get_flow_summaries")

    return [
      {
        "Name": "CallbackInbound",
        "Arn": "flow arn",
      },
      {
        "Name": "CallbackOutbound",
        "Arn": "flow arn",
      },
      {
        "Name": "CallbackAgentWhisper",
        "Arn": "flow arn",
      },
      {
        "Name": "CallbackOutboundWhisper",
        "Arn": "flow arn",
      },
    ]

  def get_contact_flow(self, flow_arn: str) -> ContactFlowTypeDef:
    """Retrieve all details of a contact flow from the ARN.

    Args:
        flow_arn (str): The ARN of the flow

    Returns:
        ContactFlowTypeDef: The contact flow details
    """
    assert flow_arn == "flow arn"
    self.calls.append("get_contact_flow")
    return {
      "Arn": "flow arn",
      "Name": "CallbackInbound",
      "Content": '{"Message":"mock flow content"}',
    }

  def start_outbound(
    self,
    flow_name: str,
    source_phone_number: str,
    destination_phone_number: str,
    attributes: dict[str, str],
  ) -> StartOutboundVoiceContactResponseTypeDef:
    """Start an outbound voice contact.

    Args:
        flow_name (str): The outbound contact flow
        source_phone_number (str): The source phone number
        destination_phone_number (str): The destination phone number
        attributes (dict[str, str]): Optional attributes to apply to the contact

    Returns:
        StartOutboundVoiceContactResponseTypeDef: The outbound voice contact response
    """
    assert flow_name == "CallbackOutbound"
    assert source_phone_number == "public"
    assert destination_phone_number == "private"
    assert attributes == {
      "CallbackId": "12345",
      "CallbackNumber": "customer",
      "CallerId": "public",
    }

    self.calls.append("start_outbound")

    return {
      "ContactId": "foo",
      "ResponseMetadata": {
        "RequestId": "request",
        "HTTPStatusCode": 200,
        "HTTPHeaders": {},
        "RetryAttempts": 0,
      },
    }

  def _get_summary(
    self,
    list_function: str,
    top_level_key: str,
    match_key: str,
    match_values: str | list[str],
    filter_predicate: Callable[[Any], bool] = lambda x: True,
    paginate_args: dict[str, str | int] = {},
  ) -> Any:
    assert False
