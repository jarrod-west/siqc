from src.deploy.deploy import deploy
from src.shared.clients.connect_client import ConnectClient
from src.shared.logger import logger
from src.shared.utils import FLOW_NAMES, read_parameters, ROUTING_PROFILE_NAME


def setup() -> None:
  parameters = read_parameters()

  logger.info("Starting setup")

  # Perform the deployment
  deploy()

  logger.info("Assigning phone number to contact flow")

  connect_client = ConnectClient(parameters["InstanceAlias"])

  # Assign the contact flow phone number
  connect_client.assign_contact_flow_number(
    FLOW_NAMES["inbound"], parameters["PrivateNumber"]
  )

  # Move the user to the routing profile
  connect_client.assign_user_to_routing_profile(
    parameters["AgentUsername"], ROUTING_PROFILE_NAME
  )

  logger.info("Setup complete")


if __name__ == "__main__":
  setup()
