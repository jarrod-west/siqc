import boto3
from dotenv import dotenv_values
import json

from src.shared import FLOW_NAMES, FLOW_EXPORT_CONTENT_DIR, FLOW_EXPORT_DIR, write_file
from src.logger import logger


def get_flow_arns(client, instance_arn):
  # Map contact flow names to their ARNs
  flows = {}

  logger.info(f"Mapping flow ARNs")
  paginator = client.get_paginator("list_contact_flows")

  for page in paginator.paginate(InstanceId=instance_arn):
    for flow in page["ContactFlowSummaryList"]:
      flows[flow["Name"]] = flow["Arn"]

  return flows


def export_flow(client, flow_name, flow_arn, instance_arn):
  logger.info(f"Exporting flow {flow_name}")

  # Describe the flow
  flow = client.describe_contact_flow(InstanceId=instance_arn, ContactFlowId=flow_arn)[
    "ContactFlow"
  ]

  # Separate out the content and save both to files
  content = flow.pop("Content")
  write_file(FLOW_EXPORT_DIR, flow_name, flow)
  write_file(FLOW_EXPORT_CONTENT_DIR, flow_name, json.loads(content))

  logger.info(f"Flow export complete")


def export():
  parameters = dotenv_values()
  instance_arn = parameters["ConnectInstanceArn"]

  # Create the target directories
  FLOW_EXPORT_CONTENT_DIR.mkdir(exist_ok=True, parents=True)

  client = boto3.client("connect")

  # Map the ids
  flow_arns = get_flow_arns(client, instance_arn)

  # Export each flow
  for flow_name in FLOW_NAMES:
    export_flow(client, flow_name, flow_arns[flow_name], instance_arn)

  logger.info("Export completed successfully")


if __name__ == "__main__":
  export()
