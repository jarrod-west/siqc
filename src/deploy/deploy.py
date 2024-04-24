import jinja2
from mypy_boto3_cloudformation.type_defs import ParameterTypeDef
from pathlib import Path
import re

from src.shared.clients.cloudformation_client import CloudformationClient
from src.shared.clients.connect_client import ConnectClient
from src.shared.logger import logger
from src.shared.utils import (
  FLOW_CONTENT_DIRECTORY,
  FLOW_STACK_CONFIG,
  InstanceConfig,
  StackConfig,
  MAIN_STACK_CONFIG,
  read_parameters,
  Parameters,
)

CAMELCASE_SPLIT_REGEX = r"([A-Z])"


def render_flows(
  flow_names: list[str], resources: dict[str, str]
) -> list[ParameterTypeDef]:
  env = jinja2.Environment(loader=jinja2.FileSystemLoader(FLOW_CONTENT_DIRECTORY))

  content_parameters: list[ParameterTypeDef] = []

  for flow_name in flow_names:
    template = env.get_template(flow_name + ".json")
    rendered = template.render(resources=resources)
    content_parameters.append(
      {"ParameterKey": f"{flow_name}Content", "ParameterValue": rendered}
    )

  return content_parameters


def create_stack_parameters(
  client: CloudformationClient,
  instance_config: InstanceConfig,
  raw_parameters: Parameters,
  template: str,
  previous_stack_resources: dict[str, str] = {},
) -> list[ParameterTypeDef]:
  parsed_template = client.validate(template)
  template_parameters: list[ParameterTypeDef] = []

  flow_content_parameters = []

  # Check which parameters the stack needs
  for parameter in parsed_template["Parameters"]:
    if parameter["ParameterKey"] in raw_parameters:
      template_parameters.append(
          {"ParameterKey": parameter["ParameterKey"], "ParameterValue": raw_parameters[parameter["ParameterKey"]]}
        )
    else:
      # Retrieve the relevant values from the instance config
      # Requires the format as "FieldNameAttribute", camelcased.  E.g. PublicNumberArn converts to instance_config.public_number["Arn"]
      *name_tokens, attribute = re.sub(
        CAMELCASE_SPLIT_REGEX, r" \1", parameter["ParameterKey"]
      ).split()

      if attribute == "Content":
        # Requires rendering flow content, will be done together at the end
        flow_content_parameters.append("".join(name_tokens))
      else:
        # Basic instance attribute config
        field_name = "_".join([token.lower() for token in name_tokens])

        # May be on the instance config or from the main stack
        field = instance_config.__getattribute__(field_name)

        # Handle case where summary field is "<Prefix>Id" or "<Prefix>Arn"
        for key in field.keys():
          if key.endswith(attribute):
            attribute = key
            break

        # Add the stack parameter
        template_parameters.append(
          {"ParameterKey": parameter["ParameterKey"], "ParameterValue": field[attribute]}
        )

  if flow_content_parameters:
    template_parameters += render_flows(
      flow_content_parameters, previous_stack_resources
    )

  return template_parameters


def deploy_stack(
  client: CloudformationClient,
  stack_config: StackConfig,
  instance_config: InstanceConfig,
  raw_parameters: Parameters,
  previous_stack_resources: dict[str, str] = {},
  iam: bool = False
) -> None:
  template = Path(stack_config.stack_template_file).read_text()

  parameters = create_stack_parameters(
    client, instance_config, raw_parameters, template, previous_stack_resources
  )

  client.deploy_stack(stack_config, template, parameters, iam)


def deploy() -> None:
  # Read parameters
  parameters = read_parameters()

  # Retrieve instance config
  logger.info("Retrieving instance config...")
  connect_client = ConnectClient(parameters["InstanceAlias"])
  phone_numbers = connect_client.get_phone_number_summaries(
    [parameters["PrivateNumber"], parameters["PublicNumber"]]
  )
  instance_config = InstanceConfig(connect_client.instance, *phone_numbers)

  cloudformation_client = CloudformationClient()

  logger.info("Deploying stacks")

  # Build the main stack
  deploy_stack(cloudformation_client, MAIN_STACK_CONFIG, instance_config, parameters, iam=True)

  # Retrieve the main stack resources
  main_stack_resources = cloudformation_client.get_stack_resource_mapping(
    MAIN_STACK_CONFIG.stack_name
  )

  # Build the flow stack
  deploy_stack(
    cloudformation_client, FLOW_STACK_CONFIG, instance_config, main_stack_resources
  )

  logger.info("Deploy complete")


if __name__ == "__main__":
  deploy()
