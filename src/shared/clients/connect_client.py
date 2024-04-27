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
  client: AwsConnectClient

  def __init__(self, instance_alias: str) -> None:
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
    return self.client.describe_contact_flow(
      InstanceId=self.instance["Arn"], ContactFlowId=flow_arn
    )["ContactFlow"]

  def assign_contact_flow_number(self, flow_name: str, phone_number: str) -> None:
    flow_summary = self.get_flow_summaries([flow_name])[0]
    number_summary = self.get_phone_number_summaries([phone_number])[0]

    self.client.associate_phone_number_contact_flow(
      InstanceId=self.instance["Arn"],
      PhoneNumberId=number_summary["PhoneNumberId"],
      ContactFlowId=flow_summary["Id"],
    )

  def unassign_contact_flow_number(self, phone_number: str) -> None:
    number_summary = self.get_phone_number_summaries([phone_number])[0]

    self.client.disassociate_phone_number_contact_flow(
      InstanceId=self.instance["Arn"],
      PhoneNumberId=number_summary["PhoneNumberId"],
    )

  def assign_user_to_routing_profile(
    self, username: str, routing_profile_name: str
  ) -> None:
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
    contact_flow_id = self.get_flow_summaries([flow_name])[0]["Id"]

    return self.client.start_outbound_voice_contact(
      InstanceId=self.instance["Id"],
      ContactFlowId=contact_flow_id,
      SourcePhoneNumber=source_phone_number,
      DestinationPhoneNumber=destination_phone_number,
      Attributes=attributes,
    )
