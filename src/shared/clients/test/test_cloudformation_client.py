from datetime import datetime
from mypy_boto3_cloudformation.type_defs import (
  ParameterTypeDef,
  StackSummaryTypeDef,
  ValidateTemplateOutputTypeDef,
  StackResourceSummaryTypeDef,
  WaiterConfigTypeDef,
)
from typing import Any

from shared.clients.cloudformation_client import CloudformationClient
from shared.clients.test.helpers import (
  mocked_client,
  AddResponseParams,
  ClientErrorParams,
  not_raises,
)
from shared.utils import DeployKwArgs, StackConfig


# Helpers
class MockWaiter:
  def __init__(
    self,
    waiter_name: str,
    expected_stack_name: str,
    expected_waiter_config: WaiterConfigTypeDef,
  ) -> None:
    self.waiter_name = waiter_name
    self.expected_stack_name = expected_stack_name
    self.expected_waiter_config = expected_waiter_config

  def wait(self, StackName: str, WaiterConfig: WaiterConfigTypeDef) -> None:
    assert StackName == self.expected_stack_name
    assert WaiterConfig == self.expected_waiter_config


# Tests
def test_get_stack_summary() -> None:
  stack1: StackSummaryTypeDef = {
    "StackName": "stack1",
    "CreationTime": datetime.now(),
    "StackStatus": "CREATE_COMPLETE",
  }
  stack2: StackSummaryTypeDef = {
    "StackName": "stack2",
    "CreationTime": datetime.now(),
    "StackStatus": "CREATE_COMPLETE",
  }

  mock_response = {
    "StackSummaries": [
      stack1,
      stack2,
    ]
  }

  client = mocked_client(
    CloudformationClient(), [AddResponseParams("list_stacks", mock_response, {})]
  )

  assert client.get_stack_summary("stack2") == stack2


def test_get_stack_resource_mapping() -> None:
  stack1: StackSummaryTypeDef = {
    "StackName": "stack1",
    "StackId": "stack1 id",
    "CreationTime": datetime.now(),
    "StackStatus": "CREATE_COMPLETE",
  }

  mock_summary_response = {
    "StackSummaries": [
      stack1,
    ]
  }

  resource1: StackResourceSummaryTypeDef = {
    "LogicalResourceId": "logical 1",
    "PhysicalResourceId": "resource 1",
    "ResourceType": "type 1",
    "LastUpdatedTimestamp": datetime.now(),
    "ResourceStatus": "CREATE_COMPLETE",
  }
  resource2: StackResourceSummaryTypeDef = {
    "LogicalResourceId": "logical 2",
    "PhysicalResourceId": "resource 2",
    "ResourceType": "type 2",
    "LastUpdatedTimestamp": datetime.now(),
    "ResourceStatus": "DELETE_COMPLETE",
  }

  mock_resource_response = {"StackResourceSummaries": [resource1, resource2]}

  client = mocked_client(
    CloudformationClient(),
    [
      AddResponseParams("list_stacks", mock_summary_response, {}),
      AddResponseParams(
        "list_stack_resources", mock_resource_response, {"StackName": "stack1 id"}
      ),
    ],
  )

  assert client.get_stack_resource_mapping("stack1") == {
    "logical 1": "resource 1",
    "logical 2": "resource 2",
  }


def test_validate() -> None:
  template_string: str = "template string"
  mock_template: ValidateTemplateOutputTypeDef = {
    "Description": "A mock template",
    "Parameters": [],
    "Capabilities": [],
    "CapabilitiesReason": "A reason",
    "DeclaredTransforms": [],
    "ResponseMetadata": {
      "RequestId": "request",
      "HTTPStatusCode": 200,
      "HTTPHeaders": {},
      "RetryAttempts": 1,
    },
  }

  client = mocked_client(
    CloudformationClient(),
    [
      AddResponseParams(
        "validate_template", mock_template, {"TemplateBody": template_string}
      )
    ],
  )

  assert client.validate(template_string) == mock_template


def test_deploy_new_stack(monkeypatch: Any) -> None:
  # Mock values
  stack1: StackSummaryTypeDef = {
    "StackName": "stack1",
    "StackId": "stack1 id",
    "CreationTime": datetime.now(),
    "StackStatus": "CREATE_COMPLETE",
  }

  mock_summary_response = {
    "StackSummaries": [
      stack1,
    ]
  }

  stack_config = StackConfig("stack2", "template file")
  template: str = "body"
  parameters: list[ParameterTypeDef] = [
    {"ParameterKey": "key1", "ParameterValue": "value1"}
  ]
  args: DeployKwArgs = {
    "StackName": "stack2",
    "TemplateBody": "body",
    "Parameters": parameters,
  }

  # Mocked client
  client = mocked_client(
    CloudformationClient(),
    [
      AddResponseParams("list_stacks", mock_summary_response, {}),
      AddResponseParams("create_stack", {}, args),
    ],
  )

  # Mock the waiter
  monkeypatch.setattr(
    client.client,
    "get_waiter",
    lambda stack_name: MockWaiter(
      stack_name,
      "stack2",
      {
        "Delay": 5,
        "MaxAttempts": 60,
      },
    ),
  )

  with not_raises():
    client.deploy_stack(stack_config, template, parameters)


def test_deploy_existing_stack(monkeypatch: Any) -> None:
  # Mock values
  stack2: StackSummaryTypeDef = {
    "StackName": "stack2",
    "StackId": "stack2 id",
    "CreationTime": datetime.now(),
    "StackStatus": "CREATE_COMPLETE",
  }

  mock_summary_response = {
    "StackSummaries": [
      stack2,
    ]
  }

  stack_config = StackConfig("stack2", "template file")
  template: str = "body"
  parameters: list[ParameterTypeDef] = [
    {"ParameterKey": "key1", "ParameterValue": "value1"}
  ]
  args: DeployKwArgs = {
    "StackName": "stack2",
    "TemplateBody": "body",
    "Parameters": parameters,
  }

  # Mocked client
  client = mocked_client(
    CloudformationClient(),
    [
      AddResponseParams("list_stacks", mock_summary_response, {}),
      AddResponseParams("update_stack", {}, args),
    ],
  )

  # Mock the waiter
  monkeypatch.setattr(
    client.client,
    "get_waiter",
    lambda stack_name: MockWaiter(
      stack_name,
      "stack2",
      {
        "Delay": 5,
        "MaxAttempts": 60,
      },
    ),
  )

  # Test changes
  with not_raises():
    client.deploy_stack(stack_config, template, parameters)


def test_deploy_existing_stack_no_changes() -> None:
  # Mock values
  stack2: StackSummaryTypeDef = {
    "StackName": "stack2",
    "StackId": "stack2 id",
    "CreationTime": datetime.now(),
    "StackStatus": "CREATE_COMPLETE",
  }

  mock_summary_response = {
    "StackSummaries": [
      stack2,
    ]
  }

  stack_config = StackConfig("stack2", "template file")
  template: str = "body"
  parameters: list[ParameterTypeDef] = [
    {"ParameterKey": "key1", "ParameterValue": "value1"}
  ]

  client = mocked_client(
    CloudformationClient(),
    [AddResponseParams("list_stacks", mock_summary_response, {})],
    [ClientErrorParams("update_stack", "", "No updates are to be performed.")],
  )

  # Test changes
  with not_raises():
    client.deploy_stack(stack_config, template, parameters)
