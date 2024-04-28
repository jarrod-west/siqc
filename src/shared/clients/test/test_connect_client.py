import boto3
from mypy_boto3_connect.type_defs import (
  InstanceSummaryTypeDef,
  ListPhoneNumbersSummaryTypeDef,
  ContactFlowSummaryTypeDef,
  ContactFlowTypeDef,
  UserSummaryTypeDef,
  RoutingProfileSummaryTypeDef,
)

from shared.clients.aws_client import AwsClient
from shared.clients.connect_client import ConnectClient
from shared.clients.test.helpers import (
  mocked_client,
  AddResponseParams,
  not_raises,
)


# Helpers
def mock_instance(alias: str) -> InstanceSummaryTypeDef:
  return {"Id": "id", "Arn": "arn", "InstanceAlias": alias}


# Constructor makes AWS calls, so need to mock it
class MockConnectClient(ConnectClient):
  def __init__(
    self, instance: InstanceSummaryTypeDef = mock_instance("instance")
  ) -> None:
    self.instance = instance
    self.client = boto3.client("connect")


def test_get_phone_number_summaries() -> None:
  # Mocks
  phone1: ListPhoneNumbersSummaryTypeDef = {
    "PhoneNumberId": "phone1",
    "PhoneNumber": "12345",
  }
  phone2: ListPhoneNumbersSummaryTypeDef = {
    "PhoneNumberId": "phone2",
    "PhoneNumber": "56789",
  }
  phone3: ListPhoneNumbersSummaryTypeDef = {
    "PhoneNumberId": "phone3",
    "PhoneNumber": "54321",
  }

  mock_summary_response = {"ListPhoneNumbersSummaryList": [phone1, phone2, phone3]}

  client = mocked_client(
    MockConnectClient(),
    [
      AddResponseParams(
        "list_phone_numbers_v2", mock_summary_response, {"InstanceId": "arn"}
      )
    ],
  )

  assert client.get_phone_number_summaries(["12345", "54321"]) == [phone1, phone3]


def test_get_flow_summaries() -> None:
  # Mocks
  flow1: ContactFlowSummaryTypeDef = {"Name": "flow1", "Arn": "arn1"}
  flow2: ContactFlowSummaryTypeDef = {"Name": "flow2", "Arn": "arn2"}
  flow3: ContactFlowSummaryTypeDef = {"Name": "flow3", "Arn": "arn3"}

  mock_summary_response = {"ContactFlowSummaryList": [flow1, flow2, flow3]}

  client = mocked_client(
    MockConnectClient(),
    [
      AddResponseParams(
        "list_contact_flows", mock_summary_response, {"InstanceId": "arn"}
      )
    ],
  )

  assert client.get_flow_summaries(["flow2", "flow3"]) == [flow2, flow3]


def test_get_contact_flow() -> None:
  mock_flow: ContactFlowTypeDef = {"Id": "id1", "Arn": "arn1", "Name": "flow1"}

  mock_flow_response = {"ContactFlow": mock_flow}

  client = mocked_client(
    MockConnectClient(),
    [
      AddResponseParams(
        "describe_contact_flow",
        mock_flow_response,
        {"InstanceId": "arn", "ContactFlowId": "arn1"},
      )
    ],
  )

  assert client.get_contact_flow("arn1") == mock_flow


def test_assign_contact_flow_number() -> None:
  # Mocks
  mock_flow: ContactFlowSummaryTypeDef = {
    "Name": "flow1",
    "Arn": "flow arn1",
    "Id": "flow id1",
  }

  mock_flow_response = {"ContactFlowSummaryList": [mock_flow]}

  mock_phone: ListPhoneNumbersSummaryTypeDef = {
    "PhoneNumberId": "phone id1",
    "PhoneNumber": "12345",
  }

  mock_summary_response = {"ListPhoneNumbersSummaryList": [mock_phone]}

  client = mocked_client(
    MockConnectClient(),
    [
      AddResponseParams(
        "list_contact_flows",
        mock_flow_response,
        {"InstanceId": "arn"},
      ),
      AddResponseParams(
        "list_phone_numbers_v2", mock_summary_response, {"InstanceId": "arn"}
      ),
      AddResponseParams(
        "associate_phone_number_contact_flow",
        {},
        {
          "InstanceId": "arn",
          "ContactFlowId": "flow id1",
          "PhoneNumberId": "phone id1",
        },
      ),
    ],
  )

  with not_raises():
    client.assign_contact_flow_number("flow1", "12345")


def test_unassign_contact_flow_number() -> None:
  # Mocks
  mock_phone: ListPhoneNumbersSummaryTypeDef = {
    "PhoneNumberId": "phone id1",
    "PhoneNumber": "12345",
  }

  mock_summary_response = {"ListPhoneNumbersSummaryList": [mock_phone]}

  client = mocked_client(
    MockConnectClient(),
    [
      AddResponseParams(
        "list_phone_numbers_v2", mock_summary_response, {"InstanceId": "arn"}
      ),
      AddResponseParams(
        "disassociate_phone_number_contact_flow",
        {},
        {"InstanceId": "arn", "PhoneNumberId": "phone id1"},
      ),
    ],
  )

  with not_raises():
    client.unassign_contact_flow_number("12345")


def test_assign_user_to_routing_profile() -> None:
  # Mocks
  mock_user: UserSummaryTypeDef = {
    "Id": "user id1",
    "Arn": "user arn1",
    "Username": "username1",
  }

  mock_routing_profile: RoutingProfileSummaryTypeDef = {
    "Name": "rp 1",
    "Id": "rp id1",
    "Arn": "rp arn1",
  }

  client = mocked_client(
    MockConnectClient(),
    [
      AddResponseParams(
        "list_users", {"UserSummaryList": [mock_user]}, {"InstanceId": "arn"}
      ),
      AddResponseParams(
        "list_routing_profiles",
        {"RoutingProfileSummaryList": [mock_routing_profile]},
        {"InstanceId": "arn"},
      ),
      AddResponseParams(
        "update_user_routing_profile",
        {},
        {"InstanceId": "arn", "RoutingProfileId": "rp id1", "UserId": "user id1"},
      ),
    ],
  )

  with not_raises():
    client.assign_user_to_routing_profile("username1", "rp 1")


def test_start_outbound() -> None:
  # Mocks
  mock_flow: ContactFlowSummaryTypeDef = {
    "Name": "flow1",
    "Arn": "flow arn1",
    "Id": "flow id1",
  }

  client = mocked_client(
    MockConnectClient(),
    [
      AddResponseParams(
        "list_contact_flows",
        {"ContactFlowSummaryList": [mock_flow]},
        {"InstanceId": "arn"},
      ),
      AddResponseParams(
        "start_outbound_voice_contact",
        {},
        {
          "InstanceId": "id",
          "ContactFlowId": "flow id1",
          "SourcePhoneNumber": "12345",
          "DestinationPhoneNumber": "54321",
          "Attributes": {"customer": "john doe"},
        },
      ),
    ],
  )

  with not_raises():
    client.start_outbound("flow1", "12345", "54321", {"customer": "john doe"})
