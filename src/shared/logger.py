import logging
import sys


def create_logger(name: str, level: int = logging.INFO) -> logging.Logger:
  """Create a logger with a specific format.

  Args:
      name (str): The name of the logger
      level (int, optional): The log level. Defaults to logging.INFO.

  Returns:
      logging.Logger: The created logger
  """
  formatter = logging.Formatter(
    fmt="%(asctime)s %(levelname)-8s %(message)s", datefmt="%Y-%m-%d %H:%M:%S"
  )
  handler = logging.StreamHandler(stream=sys.stdout)
  handler.setFormatter(formatter)
  logger = logging.getLogger(name)
  logger.setLevel(level)
  logger.addHandler(handler)
  return logger


logger = create_logger("default")
