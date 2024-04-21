from src.shared.logger import logger
from src.shared.utils import read_parameters


def teardown() -> None:
  parameters = read_parameters()

  logger.info("Starting teardown")

  logger.info("Unassigning phone number from contact flow")
  

  logger.info("Teardown complete")


if __name__ == "__main__":
  teardown()