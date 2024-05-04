from mypy_boto3_connect.type_defs import (
  InstanceSummaryTypeDef,
  ListPhoneNumbersSummaryTypeDef,
)
from pytest_mock import MockerFixture

from shared.utils import create_logical_id, read_parameters, InstanceConfig


def test_read_parameters(mocker: MockerFixture) -> None:
  mock_parameters = {
    "InstanceAlias": "alias",
    "PrivateNumber": "private",
    "PublicNumber": "public",
    "AgentUsername": "agent",
    "CustomerNumber": "customer",
    "DefaultRoutingProfile": "routing",
  }

  mocker.patch("dotenv.dotenv_values", return_value=mock_parameters)

  parameters = read_parameters()

  assert parameters == mock_parameters
  assert parameters["CallerId"] == "public"

  mock_parameters["CallerId"] = "caller id"

  mocker.patch("dotenv.dotenv_values", return_value=mock_parameters)

  parameters = read_parameters()

  assert parameters == mock_parameters
  assert parameters["CallerId"] == "caller id"


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
