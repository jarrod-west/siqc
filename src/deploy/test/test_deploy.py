import jinja2
from pathlib import Path
from pytest_mock import MockerFixture
from typing import cast

from deploy.deploy import deploy, deploy_stack
from shared.test_helpers.helpers import (
  MockCloudformationClient,
  MockConnectClient,
  not_raises,
)
from mypy_boto3_connect.type_defs import (
  InstanceSummaryTypeDef,
  ListPhoneNumbersSummaryTypeDef,
)
from shared.clients import cloudformation_client, connect_client
from shared.utils import StackConfig, InstanceConfig


class MockJinja2FileSystemLoader(jinja2.FileSystemLoader):
  def __init__(self, searchpath: str) -> None:
    super().__init__(f"../{searchpath}")


def instance_config() -> InstanceConfig:
  mock_instance_summery: InstanceSummaryTypeDef = {
    "Id": "instance id",
    "Arn": "instance arn",
  }
  mock_private_number: ListPhoneNumbersSummaryTypeDef = {
    "PhoneNumber": "number 1",
    "PhoneNumberArn": "private arn",
  }
  mock_public_number: ListPhoneNumbersSummaryTypeDef = {
    "PhoneNumber": "number 2",
    "PhoneNumberArn": "public arn",
  }
  return InstanceConfig(mock_instance_summery, mock_private_number, mock_public_number)


def test_deploy_stack(mocker: MockerFixture) -> None:
  mock_client = MockCloudformationClient()
  mock_stack_config = StackConfig("stack1", "template location 1")
  mock_instance_config = instance_config()

  previous_stack_resources = {
    "PublicNumberArn": "public arn",
  }

  mocker.patch.object(Path, "read_text", return_value="template body")

  assert deploy_stack(
    cast(cloudformation_client.CloudformationClient, mock_client),
    mock_stack_config,
    mock_instance_config,
    previous_stack_resources,
  ) == {
    "new resource 1": "new arn1",
    "new resource 2": "new arn2",
  }

  assert mock_client.calls == [
    "__init__",
    "validate",
    "deploy_stack",
    "get_stack_resource_mapping",
  ]


def test_deploy(mocker: MockerFixture) -> None:
  mock_parameters = {
    "InstanceAlias": "alias",
    "PrivateNumber": "private",
    "PublicNumber": "public",
    "AgentUsername": "agent",
    "CustomerNumber": "customer",
    "DefaultRoutingProfile": "routing",
  }

  mocker.patch("dotenv.dotenv_values", return_value=mock_parameters)

  mock_cloudformation_client = MockCloudformationClient(False)
  mocker.patch.object(
    cloudformation_client.CloudformationClient,
    "__new__",
    return_value=mock_cloudformation_client,
  )
  mock_connect_client = MockConnectClient("alias")
  mocker.patch.object(
    connect_client.ConnectClient, "__new__", return_value=mock_connect_client
  )

  mocker.patch.object(Path, "read_text", return_value="template body")

  with not_raises():
    deploy()

  assert len(mock_cloudformation_client.calls) == 10
  assert mock_connect_client.calls == ["__init__", "get_phone_number_summaries"]
