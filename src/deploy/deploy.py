import jinja2
from mypy_boto3_cloudformation.type_defs import ParameterTypeDef
from pathlib import Path
import re

from shared.clients.cloudformation_client import CloudformationClient
from shared.clients.connect_client import ConnectClient
from shared.logger import logger
from shared.utils import (
  FLOW_CONTENT_DIRECTORY,
  CALLBACK_FLOW_STACK_CONFIG,
  WHISPER_FLOW_STACK_CONFIG,
  InstanceConfig,
  StackConfig,
  MAIN_STACK_CONFIG,
  read_parameters,
)

CAMELCASE_SPLIT_REGEX = r"([A-Z])"


def render_flows(
  flow_names: list[str], resources: dict[str, str]
) -> list[ParameterTypeDef]:
  """Renders the jinja2-templated contact flow content, replacing name values with ARNs.

  Args:
      flow_names (list[str]): List of flows to render, by name
      resources (dict[str, str]): Map of resource ARNs to common names

  Returns:
      list[ParameterTypeDef]: A list of cloudformation parameters containing the rendered contact flow content.
  """
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
  template: str,
  previous_stack_resources: dict[str, str] = {},
) -> list[ParameterTypeDef]:
  """General function to create the cloudformation parameters from instance configuration, rendered contact flows, or other stack's resources.

  Args:
      client (CloudformationClient): The cloudformation client
      instance_config (InstanceConfig): Connect instance configuration, for instance-specific parameters
      template (str): The cloudformation template, used to retrieve the parameters
      previous_stack_resources (dict[str, str], optional): Resources from earlier stack deployments, as a map of name to ARN. Defaults to {}.

  Returns:
      list[ParameterTypeDef]: A list of cloudformation parameters containing the combined parameters.
  """
  parsed_template = client.validate(template)
  template_parameters: list[ParameterTypeDef] = []

  flow_content_parameters = []

  # Check which parameters the stack needs
  for parameter in parsed_template["Parameters"]:
    # Retrieve the relevant values from the instance config
    # Requires the format as "FieldNameAttribute", camelcased.  E.g. PublicNumberArn converts to instance_config.public_number["Arn"]
    *name_tokens, attribute = re.sub(
      CAMELCASE_SPLIT_REGEX, r" \1", parameter["ParameterKey"]
    ).split()

    name_without_attribute = "".join(name_tokens)

    if attribute == "Content":
      # Requires rendering flow content, will be done together at the end
      flow_content_parameters.append(name_without_attribute)
    else:
      value: str

      if name_without_attribute in previous_stack_resources:
        value = previous_stack_resources[name_without_attribute]
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

        value = field[attribute]

      # Add the stack parameter
      template_parameters.append(
        {
          "ParameterKey": parameter["ParameterKey"],
          "ParameterValue": value,
        }
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
  previous_stack_resources: dict[str, str] = {},
) -> dict[str, str]:
  """Deploy a single cloudformation stack.

  Args:
      client (CloudformationClient): The cloudformation client
      stack_config (StackConfig): Stack-specific configuration, including the name and location of the template
      instance_config (InstanceConfig): Connect instance configuration
      previous_stack_resources (dict[str, str], optional): Resources from earlier stack deployments, as a map of name to ARN. Defaults to {}.

  Returns:
      dict[str, str]: Resources from this stack, as a map of name to ARN
  """
  template = Path(stack_config.stack_template_file).read_text()

  parameters = create_stack_parameters(
    client, instance_config, template, previous_stack_resources
  )

  client.deploy_stack(stack_config, template, parameters)

  return client.get_stack_resource_mapping(stack_config.stack_name)


def deploy() -> None:
  """Deploys all the system's cloudformation stacks."""
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

  created_resources = deploy_stack(
    cloudformation_client, WHISPER_FLOW_STACK_CONFIG, instance_config
  )

  # Build the main stack
  created_resources.update(
    deploy_stack(
      cloudformation_client, MAIN_STACK_CONFIG, instance_config, created_resources
    )
  )

  # Build the callback flow stack
  deploy_stack(
    cloudformation_client,
    CALLBACK_FLOW_STACK_CONFIG,
    instance_config,
    created_resources,
  )

  logger.info("Deploy complete")


if __name__ == "__main__":
  deploy()
