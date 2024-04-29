from shared.clients import connect_client
from shared.logger import logger
from shared.utils import read_parameters


def teardown() -> None:
  """Teardown the system, unassigning resources.  Note: doesn't delete the stacks."""
  parameters = read_parameters()

  logger.info("Starting teardown")

  logger.info("Unassigning phone number from contact flow")

  # Unassign the contact flow phone number
  client = connect_client.ConnectClient(parameters["InstanceAlias"])
  client.unassign_contact_flow_number(parameters["PrivateNumber"])

  # Move the user to the default routing profile
  client.assign_user_to_routing_profile(
    parameters["AgentUsername"], parameters["DefaultRoutingProfile"]
  )

  logger.info("Teardown complete")


if __name__ == "__main__":
  teardown()
