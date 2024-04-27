import logging

from shared.logger import create_logger


def test_create_logger() -> None:
  logger = create_logger("test_logger")
  assert logger
  assert logger.level == logging.INFO
