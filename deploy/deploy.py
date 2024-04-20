import boto3
import botocore
import botocore.client
from dotenv import dotenv_values
import jinja2
import json
from pathlib import Path

from src.shared import CLOUDFORMATION_TEMPLATE, FLOW_DEPLOY_DIR, FLOW_DEPLOY_CONTENT_DIR, logical_id, untemplate_filename
from src.logger import logger

MAIN_STACK_NAME = "sicq-main-stack"
FLOW_STACK_NAME = "sicq-flow-stack"
TEMPLATE_FILE = "./deploy/cloudformation.yaml"

def stack_id(client, stack_name):
  paginator = client.get_paginator("list_stacks")

  # Iterate through stack summaries to check if name exists
  for page in paginator.paginate():
    for stack in page["StackSummaries"]:
      if stack["StackStatus"] != "DELETE_COMPLETE" and stack["StackName"] == stack_name:
        return stack["StackId"]

  return None

def stack_exists(client, stack_name):
  return stack_id(client, stack_name) is not None


def deploy_stack(client, stack_name, template, parameters):
  # Cloudformation has different deployment types depending on whether the stack already exists
  if stack_exists(client, stack_name):
    deployment_function = client.update_stack
    waiter = client.get_waiter("stack_update_complete")
  else:
    deployment_function = client.create_stack
    waiter = client.get_waiter("stack_create_complete")

  logger.info("Starting deployment...")

  # Do the deployment
  try:
    deployment_function(
      StackName=stack_name,
      TemplateBody=template,
      Parameters=[{"ParameterKey": p[0], "ParameterValue": p[1]} for p in parameters.items()]
    )
  except botocore.client.ClientError:
    logger.info("No changes to deploy")
    return

  # Wait for the deployment to finish
  waiter.wait(
    StackName=stack_name,
    WaiterConfig={
      "Delay": 5,
      "MaxAttempts": 60 # 5 Minutes
    }
  )

  logger.info("Deployment complete")

def render_flow_template(client):
  # Retrieve the main stack resources
  stack_resources = client.list_stack_resources(
    StackName=stack_id(client, MAIN_STACK_NAME)
  )["StackResourceSummaries"]

  # Create the logical ID -> ARN mapping
  resources = {}

  for stack_resource in stack_resources:
    resources[stack_resource["LogicalResourceId"]] = stack_resource["PhysicalResourceId"]

  # Render the content templates
  env = jinja2.Environment(loader=jinja2.FileSystemLoader(FLOW_DEPLOY_CONTENT_DIR))

  content = {}
  for file in FLOW_DEPLOY_CONTENT_DIR.iterdir():
    template = env.get_template(file.name)
    rendered = template.render(resources=resources)
    content[logical_id(file.stem)] = json.dumps(json.loads(rendered))

  # Render the complete template
  env = jinja2.Environment(loader=jinja2.FileSystemLoader(FLOW_DEPLOY_DIR))
  template = env.get_template(CLOUDFORMATION_TEMPLATE)

  return template.render(content=content)


def deploy():
  # Read parameter and template files
  parameters = dotenv_values()
  main_template = Path(TEMPLATE_FILE).read_text()

  # Create the cloudformation client
  client = boto3.client('cloudformation')

  # Deploy the main stack
  deploy_stack(client, MAIN_STACK_NAME, main_template, parameters)

  # Render the flow stack
  flow_template = render_flow_template(client)
  with open(FLOW_DEPLOY_DIR.joinpath(untemplate_filename(CLOUDFORMATION_TEMPLATE)), "w") as outfile:
    outfile.write(flow_template)

  deploy_stack(client, FLOW_STACK_NAME, flow_template, parameters)


if __name__ == '__main__':
  deploy()
