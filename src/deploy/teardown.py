from src.shared.clients.connect_client import ConnectClient
from src.shared.logger import logger
from src.shared.utils import read_parameters


def teardown() -> None:
  parameters = read_parameters()

  logger.info("Starting teardown")

  logger.info("Unassigning phone number from contact flow")

  # Unassign the contact flow phone number
  connect_client = ConnectClient(parameters["InstanceAlias"])
  connect_client.unassign_contact_flow_number(parameters["PrivateNumber"])

  # Move the user to the default routing profile
  connect_client.assign_user_to_routing_profile(
    parameters["AgentUsername"], parameters["DefaultRoutingProfile"]
  )

  logger.info("Teardown complete")


if __name__ == "__main__":
  teardown()
