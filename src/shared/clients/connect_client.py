from mypy_boto3_connect.type_defs import (
  ContactFlowSummaryTypeDef,
  ContactFlowTypeDef,
  InstanceSummaryTypeDef,
  ListPhoneNumbersSummaryTypeDef,
  StartOutboundVoiceContactResponseTypeDef,
)
from mypy_boto3_connect.client import ConnectClient as AwsConnectClient
from typing import Any, Callable, cast

from shared.clients.aws_client import AwsClient


class ConnectClient(AwsClient):
  """A client to perform connect operations.

  Args:
      AwsClient (_type_): The underlying AWS client
  """

  client: AwsConnectClient

  def __init__(self, instance_alias: str) -> None:
    """Constuctor.

    Args:
        instance_alias (str): The alias of the relevant Connect instance
    """
    super().__init__("connect")
    self.instance = cast(
      InstanceSummaryTypeDef,
      super()._get_summary(
        "list_instances", "InstanceSummaryList", "InstanceAlias", instance_alias
      ),
    )

  def _get_summary(
    self,
    list_function: str,
    top_level_key: str,
    match_key: str,
    match_values: str | list[str],
    filter_predicate: Callable[[Any], bool] = lambda x: True,
    paginate_args: dict[str, str | int] = {},
  ) -> Any:
    """Wrapper around the general get_summary function which automatically adds the InstanceId to the paginator arguments.

    Args:
        list_function (str): The name of the function to call
        top_level_key (str): The response key that contains the resource summaries
        match_key (str): The key of a comparator used to filter the results
        match_values (str | list[str]): The value or values of the comparator used to filter the results
        filter_predicate (_type_, optional): Extra check to filter out responses. Defaults to lambda x:True.
        paginate_args (dict[str, str  |  int], optional): Arguments to parse to the paginator. Defaults to {}.


    Returns:
        Any: A list of the summary-type responses for the AWS resources that match the filter
    """
    # Add the instance ARN to all pagination requests.  Note that it has different names, e.g. InstanceArn, InstanceId, etc
    args = {"InstanceId": self.instance["Arn"], **paginate_args}

    return super()._get_summary(
      list_function,
      top_level_key,
      match_key,
      match_values,
      filter_predicate,
      args,
    )

  def get_phone_number_summaries(
    self, phone_numbers: list[str]
  ) -> list[ListPhoneNumbersSummaryTypeDef]:
    """Retrieve the summaries of instance phone numbers matching the given values.

    Args:
        phone_numbers (list[str]): A list of phone numbers in E.164 format

    Returns:
        list[ListPhoneNumbersSummaryTypeDef]: The summaries of the matching phone numbers
    """
    return cast(
      list[ListPhoneNumbersSummaryTypeDef],
      self._get_summary(
        "list_phone_numbers_v2",
        "ListPhoneNumbersSummaryList",
        "PhoneNumber",
        phone_numbers,
      ),
    )

  def get_flow_summaries(
    self, flow_names: list[str]
  ) -> list[ContactFlowSummaryTypeDef]:
    """Retrieve the summaries of instance contact flows matching the given names.

    Args:
        flow_names (list[str]): A list of contact flow names

    Returns:
        list[ContactFlowSummaryTypeDef]: The summaries of the contact flows
    """
    return cast(
      list[ContactFlowSummaryTypeDef],
      self._get_summary(
        "list_contact_flows",
        "ContactFlowSummaryList",
        "Name",
        flow_names,
      ),
    )

  def get_contact_flow(self, flow_arn: str) -> ContactFlowTypeDef:
    """Retrieve all details of a contact flow from the ARN.

    Args:
        flow_arn (str): The ARN of the flow

    Returns:
        ContactFlowTypeDef: The contact flow details
    """
    return self.client.describe_contact_flow(
      InstanceId=self.instance["Arn"], ContactFlowId=flow_arn
    )["ContactFlow"]

  def assign_contact_flow_number(self, flow_name: str, phone_number: str) -> None:
    """Assign a phone number to a contact flow.

    Args:
        flow_name (str): The name of the contact flow
        phone_number (str): The phone number in E.164 format
    """
    flow_summary = self.get_flow_summaries([flow_name])[0]
    number_summary = self.get_phone_number_summaries([phone_number])[0]

    self.client.associate_phone_number_contact_flow(
      InstanceId=self.instance["Arn"],
      PhoneNumberId=number_summary["PhoneNumberId"],
      ContactFlowId=flow_summary["Id"],
    )

  def unassign_contact_flow_number(self, phone_number: str) -> None:
    """Remove a phone number from a contact flow.

    Args:
        phone_number (str): The phone number in E.164 format
    """
    number_summary = self.get_phone_number_summaries([phone_number])[0]

    self.client.disassociate_phone_number_contact_flow(
      InstanceId=self.instance["Arn"],
      PhoneNumberId=number_summary["PhoneNumberId"],
    )

  def assign_user_to_routing_profile(
    self, username: str, routing_profile_name: str
  ) -> None:
    """Assign a Connect user to a routing profile.

    Args:
        username (str): The username of the user
        routing_profile_name (str): The name of the routing profile
    """
    user_summary = self._get_summary(
      "list_users", "UserSummaryList", "Username", username
    )
    routing_profile_summary = self._get_summary(
      "list_routing_profiles", "RoutingProfileSummaryList", "Name", routing_profile_name
    )

    self.client.update_user_routing_profile(
      InstanceId=self.instance["Arn"],
      RoutingProfileId=routing_profile_summary["Id"],
      UserId=user_summary["Id"],
    )

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
    contact_flow_id = self.get_flow_summaries([flow_name])[0]["Id"]

    return self.client.start_outbound_voice_contact(
      InstanceId=self.instance["Id"],
      ContactFlowId=contact_flow_id,
      SourcePhoneNumber=source_phone_number,
      DestinationPhoneNumber=destination_phone_number,
      Attributes=attributes,
    )
