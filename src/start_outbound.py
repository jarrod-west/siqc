from shared.clients.connect_client import ConnectClient
from shared.logger import logger
from shared.utils import FLOW_NAMES, read_parameters


def start_outbound() -> None:
  """Start an outbound call using parameters from the .env file."""
  # Read parameters and retrieve values
  parameters = read_parameters()

  connect_client = ConnectClient(parameters["InstanceAlias"])

  logger.info("Starting outbound call")

  response = connect_client.start_outbound(
    FLOW_NAMES["outbound"],
    parameters["PublicNumber"],
    parameters["PrivateNumber"],
    {
      "CallbackId": "12345",
      "CallbackNumber": parameters["CustomerNumber"],
      "CallerId": parameters["CallerId"],
    },
  )

  logger.info(f"Outbound call started with ContactID={response['ContactId']}")


if __name__ == "__main__":
  start_outbound()
