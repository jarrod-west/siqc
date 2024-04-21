from src.deploy.deploy import deploy
from src.shared.clients.connect_client import ConnectClient
from src.shared.logger import logger
from src.shared.utils import read_parameters


def setup() -> None:
  parameters = read_parameters()

  logger.info("Starting setup")

  # Perform the deployment
  deploy()

  logger.info("Assigning phone number to contact flow")

  # Assign the contact flow phone number
  connect_client = ConnectClient(parameters["InstanceAlias"])
  connect_client.assign_contact_flow_number(
    "CallbackInbound", parameters["PrivateNumber"]
  )

  logger.info("Setup complete")


if __name__ == "__main__":
  setup()
