import dotenv
from mypy_boto3_connect.type_defs import (
  InstanceSummaryTypeDef,
  ListPhoneNumbersSummaryTypeDef,
)

from typing import Any
from shared.utils import create_logical_id, read_parameters, InstanceConfig


def test_read_parameters(monkeypatch: Any) -> None:
  mock_val = {
    "InstanceAlias": "alias",
    "PrivateNumber": "private",
    "PublicNumber": "public",
    "AgentUsername": "agent",
    "CustomerNumber": "customer",
    "DefaultRoutingProfile": "routing",
  }

  monkeypatch.setattr(dotenv, "dotenv_values", lambda: mock_val)

  parameters = read_parameters()

  assert parameters == mock_val


def test_create_logical_id() -> None:
  assert create_logical_id("Test Logical Value") == "TestLogicalValue"
  assert create_logical_id("test-logical-value") == "TestLogicalValue"
  assert create_logical_id("Test_logical-value") == "TestLogicalValue"


def test_instance_config() -> None:
  mock_instance_summery: InstanceSummaryTypeDef = {"Id": "InstanceSummary"}
  mock_private_number: ListPhoneNumbersSummaryTypeDef = {"PhoneNumber": "Number1"}
  mock_public_number: ListPhoneNumbersSummaryTypeDef = {"PhoneNumber": "Number2"}
  config = InstanceConfig(
    mock_instance_summery, mock_private_number, mock_public_number
  )

  assert config.instance == mock_instance_summery
  assert config.private_number == mock_private_number
  assert config.public_number == mock_public_number
