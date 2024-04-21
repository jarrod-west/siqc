import logging
import sys


def create_logger(name: str, level: int = logging.INFO) -> logging.Logger:
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
