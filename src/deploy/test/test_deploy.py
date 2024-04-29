import jinja2
from pathlib import Path
from typing import Any, cast

from deploy.deploy import deploy_stack
from deploy.test.helpers import MockCloudformationClient
from mypy_boto3_connect.type_defs import (
  InstanceSummaryTypeDef,
  ListPhoneNumbersSummaryTypeDef,
)
from shared.clients.cloudformation_client import CloudformationClient
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


def test_deploy_stack(monkeypatch: Any) -> None:
  mock_client = MockCloudformationClient()
  mock_stack_config = StackConfig("stack1", "template location 1")
  mock_instance_config = instance_config()

  previous_stack_resources = {
    "PreviousResource1": "previous arn1",
    "PreviousResource2": "previous arn2",
  }

  monkeypatch.setattr(Path, "read_text", lambda _: "template body")

  assert deploy_stack(
    cast(CloudformationClient, mock_client),
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


# def test_deploy(monkeypatch: Any) -> None:
#   mock_cloudformation_client = MockCloudformationClient()
#   mock_connect_client = MockConnectClient("alias")

#   mock_parameters = {
#     "InstanceAlias": "alias",
#     "PrivateNumber": "private",
#     "PublicNumber": "public",
#     "AgentUsername": "agent",
#     "CustomerNumber": "customer",
#     "DefaultRoutingProfile": "routing",
#   }

#   monkeypatch.setattr(dotenv, "dotenv_values", lambda: mock_parameters)

#   monkeypatch.setattr(
#     CloudformationClient, "__new__", lambda _: mock_cloudformation_client
#   )
#   monkeypatch.setattr(ConnectClient, "__new__", lambda _x, _y: mock_connect_client)
#   monkeypatch.setattr(Path, "read_text", lambda _: "template body")

#   # with not_raises():
#   deploy()
