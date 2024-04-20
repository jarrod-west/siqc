import boto3
import botocore
import botocore.client
from dotenv import dotenv_values
from pathlib import Path

from src.logger import logger

STACK_NAME = "sicq-demo-stack"
TEMPLATE_FILE = "./deploy/cloudformation.yaml"

def stack_exists(client):
  paginator = client.get_paginator("list_stacks")

  # Iterate through stack summaries to check if name exists
  for page in paginator.paginate():
    for stack in page["StackSummaries"]:
      if stack["StackName"] == STACK_NAME:
        return True

  return False

def deploy():
  # Read parameter and template files
  parameters = dotenv_values()
  template = Path(TEMPLATE_FILE).read_text()

  # Create the cloudformation client
  client = boto3.client('cloudformation')

  if stack_exists(client):
    deployment_function = client.update_stack
    waiter = client.get_waiter("stack_update_complete")
  else:
    deployment_function = client.create_stack
    waiter = client.get_waiter("stack_create_complete")

  logger.info("Starting deployment...")

  try:
    deployment_function(
      StackName=STACK_NAME,
      TemplateBody=template,
      Parameters=[{"ParameterKey": p[0], "ParameterValue": p[1]} for p in parameters.items()]
    )
  except botocore.client.ClientError:
    logger.info("No changes to deploy")
    return

  waiter.wait(
    StackName=STACK_NAME,
    WaiterConfig={
      "Delay": 5,
      "MaxAttempts": 100 # 5 Minutes
    }
  )

  logger.info("Deployment complete")


if __name__ == '__main__':
  deploy()
