from pathlib import Path
from mypy_boto3_cloudformation.type_defs import ParameterTypeDef
import re

from src.shared.clients.cloudformation_client import CloudformationClient
from src.shared.clients.connect_client import ConnectClient
from src.shared.utils import (
  InstanceConfig,
  StackConfig,
  MAIN_STACK_CONFIG,
  read_parameters,
)

CAMELCASE_SPLIT_REGEX = r"([A-Z])"


def create_stack_parameters(
  client: CloudformationClient, instance_config: InstanceConfig, template: str
) -> list[ParameterTypeDef]:
  parsed_template = client.validate(template)
  template_parameters: list[ParameterTypeDef] = []

  # Check which parameters the stack needs
  for parameter in parsed_template["Parameters"]:
    # Retrieve the relevant values from the instance config
    # Requires the format as "FieldNameAttribute", camelcased.  E.g. PublicNumberArn converts to instance_config.public_number["Arn"]
    *name_tokens, attribute = re.sub(
      CAMELCASE_SPLIT_REGEX, r" \1", parameter["ParameterKey"]
    ).split()

    field_name = "_".join([token.lower() for token in name_tokens])
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

  return template_parameters


def deploy_stack(
  client: CloudformationClient,
  stack_config: StackConfig,
  instance_config: InstanceConfig,
) -> None:
  template = Path(stack_config.stack_template_file).read_text()

  parameters = create_stack_parameters(client, instance_config, template)

  client.deploy_stack(stack_config, template, parameters)


def deploy() -> None:
  # Read parameters
  parameters = read_parameters()

  # Retrieve instance config
  connect_client = ConnectClient(parameters["InstanceAlias"])
  phone_numbers = connect_client.get_phone_number_summaries(
    [parameters["PrivateNumber"], parameters["PublicNumber"]]
  )
  instance_config = InstanceConfig(connect_client.instance, *phone_numbers)

  cloudformation_client = CloudformationClient()

  # Build the main stack
  deploy_stack(cloudformation_client, MAIN_STACK_CONFIG, instance_config)


if __name__ == "__main__":
  deploy()
