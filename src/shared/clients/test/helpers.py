from botocore.stub import Stubber
from contextlib import contextmanager
from typing import Any, Mapping, overload, TypeVar, Union

from shared.clients.cloudformation_client import CloudformationClient
from shared.clients.connect_client import ConnectClient

ClientType = TypeVar("ClientType")


class AddResponseParams:
  """Helper to store botocore stubbed function arguments."""

  mocked_function: str
  mocked_response: Mapping[str, Any]
  expected_params: Mapping[str, Any]

  def __init__(
    self,
    mocked_function: str,
    mocked_response: Mapping[str, Any],
    expected_params: Mapping[str, Any],
  ) -> None:
    """Constructor.

    Args:
        mocked_function (str): The name of the mocked function
        mocked_response (str): The response from the mock function
        expected_params (str): The expected input parameters to the mock function
    """
    self.mocked_function = mocked_function
    self.mocked_response = mocked_response
    self.expected_params = expected_params


class ClientErrorParams:
  """Helper to store botocore stubbed error arguments."""

  mocked_function: str
  error_code: str
  error_message: str

  def __init__(
    self,
    mocked_function: str,
    error_code: str,
    error_message: str,
  ) -> None:
    """Constructor.

    Args:
        mocked_function (str): The name of the mocked function
        error_code (str): The code of the thrown error
        error_message (str): The message of the thrown error
    """
    self.mocked_function = mocked_function
    self.error_code = error_code
    self.error_message = error_message


@overload
def mocked_client(
  client: CloudformationClient,
  add_response_params: list[AddResponseParams],
  client_error_params: list[ClientErrorParams] = [],
) -> CloudformationClient:
  pass


@overload
def mocked_client(
  client: ConnectClient,
  add_response_params: list[AddResponseParams],
  client_error_params: list[ClientErrorParams] = [],
) -> ConnectClient:
  pass


def mocked_client(
  client: Union[CloudformationClient, ConnectClient],
  add_response_params: list[AddResponseParams],
  client_error_params: list[ClientErrorParams] = [],
) -> Union[CloudformationClient, ConnectClient]:
  """Creates a mocked client with the provided mocked functions and errors.

  Args:
      client (AwsClient): The client to mock
      add_response_params (list[AddResponseParams]): List of responses to mock
      client_error_params (list[ClientErrorParams], optional): List of errors to mock. Defaults to [].

  Returns:
      ClientType: The mocked client
  """
  stub = Stubber(client.client)

  for add_response in add_response_params:
    stub.add_response(
      add_response.mocked_function,
      add_response.mocked_response,
      add_response.expected_params,
    )

  for client_error in client_error_params:
    stub.add_client_error(
      client_error.mocked_function, client_error.error_code, client_error.error_message
    )

  stub.activate()

  return client


@contextmanager
def not_raises() -> Any:
  """Helper context to explicitly check function doesn't raise an error.

  Raises:
      AssertionError: Thrown when any error occurs within the context

  Returns:
      Any: The context
  """
  try:
    yield
  except Exception as error:
    raise AssertionError(f"An unexpected exception {error} raised.")
