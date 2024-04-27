import botocore
from mypy_boto3_cloudformation.client import (
  CloudFormationClient as AwsCloudFormationClient,
)
from mypy_boto3_cloudformation.type_defs import (
  ParameterTypeDef,
  StackSummaryTypeDef,
  ValidateTemplateOutputTypeDef,
)
from mypy_boto3_cloudformation.waiter import (
  StackCreateCompleteWaiter,
  StackUpdateCompleteWaiter,
)
from typing import cast

from shared.utils import DeployKwArgs, StackConfig
from shared.logger import logger
from shared.clients.aws_client import AwsClient


class CloudformationClient(AwsClient):
  """A client to perform cloudformation operations.

  Args:
      AwsClient (_type_): The underlying AWS client
  """

  client: AwsCloudFormationClient

  def __init__(self) -> None:
    """Constructor."""
    super().__init__("cloudformation")

  def get_stack_summary(self, stack_name: str) -> StackSummaryTypeDef:
    """Retrieve the summary of a stack matching the given name.

    Args:
        stack_name (str): The name of the stack

    Returns:
        StackSummaryTypeDef: The summary of the stack
    """
    return cast(
      StackSummaryTypeDef,
      self._get_summary(
        "list_stacks",
        "StackSummaries",
        "StackName",
        stack_name,
        lambda x: x["StackStatus"] != "DELETE_COMPLETE",
      ),
    )

  def get_stack_resource_mapping(self, stack_name: str) -> dict[str, str]:
    """Retrieve a mapping of a stack's resources by logical name to ARN.

    Args:
        stack_name (str): The name of the stack

    Returns:
        dict[str, str]: A mapping of resources by logical name to ARN.
    """
    summary = self.get_stack_summary(stack_name)

    resource_map: dict[str, str] = {}

    stack_resources = self.client.list_stack_resources(StackName=summary["StackId"])[
      "StackResourceSummaries"
    ]

    for stack_resource in stack_resources:
      resource_map[stack_resource["LogicalResourceId"]] = stack_resource[
        "PhysicalResourceId"
      ]

    return resource_map

  def _stack_exists(self, stack_name: str) -> bool:
    """Helper to check if a stack exists.

    Args:
        stack_name (str): The name of the stack

    Returns:
        bool: True if it exists, False otherwise
    """
    return self.get_stack_summary(stack_name) is not None

  def validate(self, template: str) -> ValidateTemplateOutputTypeDef:
    """Validate a cloudformation template, which also parses the parameters.

    Args:
        template (str): The cloudformation template.

    Returns:
        ValidateTemplateOutputTypeDef: The stack validation object, including parameters
    """
    return self.client.validate_template(TemplateBody=template)

  def deploy_stack(
    self,
    stack_config: StackConfig,
    template: str,
    parameters: list[ParameterTypeDef],
  ) -> None:
    """Deploy a stack from a cloudformation template with the provided parameters.

    Args:
        stack_config (StackConfig): General stack configuration
        template (str): The cloudformation template
        parameters (list[ParameterTypeDef]): Parameters for the stack

    Raises:
        ex: botocore.client.ClientError other than "No updates are to be performed"
    """
    # Set the function call args
    kwargs: DeployKwArgs = {
      "StackName": stack_config.stack_name,
      "TemplateBody": template,
      "Parameters": parameters,
    }

    # Do the deployment
    logger.info(f"Starting deployment of {stack_config.stack_name}...")

    # Different waiter and function depending on create/update
    waiter: StackCreateCompleteWaiter | StackUpdateCompleteWaiter

    try:
      if self._stack_exists(stack_config.stack_name):
        waiter = self.client.get_waiter("stack_update_complete")
        self.client.update_stack(**kwargs)
      else:
        waiter = self.client.get_waiter("stack_create_complete")
        self.client.create_stack(**kwargs)

    except botocore.client.ClientError as ex:
      if ex.response["Error"]["Message"] == "No updates are to be performed.":
        logger.info("No changes to deploy")
        return

      raise ex

    # Wait for the deployment to finish
    waiter.wait(
      StackName=stack_config.stack_name,
      WaiterConfig={
        "Delay": 5,
        "MaxAttempts": 60,  # 5 Minutes
      },
    )

    logger.info("Deployment complete")
