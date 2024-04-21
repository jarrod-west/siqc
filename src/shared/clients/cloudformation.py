import botocore
from mypy_boto3_cloudformation.type_defs import ParameterTypeDef, StackSummaryTypeDef, ValidateTemplateOutputTypeDef

from src.shared.utils import StackConfig
from src.shared.logger import logger
from src.shared.clients.aws_client import AwsClient

class CloudformationClient(AwsClient):
  def __init__(self) -> None:
    super().__init__("cloudformation")

  def get_stack_summary(self, stack_name: str) -> StackSummaryTypeDef:
    return self._get_summary("list_stacks", "StackSummaries", "StackName", stack_name, lambda x: x["StackStatus"] != "DELETE_COMPLETE")

  def _stack_exists(self, stack_name: str) -> bool:
    return self.get_stack_summary(stack_name) is not None

  def validate(self, template: str) -> ValidateTemplateOutputTypeDef:
    return self.client.validate_template(TemplateBody=template)

  def deploy_stack(self, stack_config: StackConfig, template: str, parameters: ParameterTypeDef) -> None:
    # Determine the function to call...
    if self._stack_exists(stack_config.stack_name):
      deployment_function = self.client.update_stack
      waiter = self.client.get_waiter("stack_update_complete")
    else:
      deployment_function = self.client.create_stack
      waiter = self.client.get_waiter("stack_create_complete")

    logger.info(f"Starting deployment of {stack_config.stack_name}...")

    # Do the deployment
    try:
      deployment_function(
        StackName=stack_config.stack_name,
        TemplateBody=template,
        Parameters=parameters,
      )
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