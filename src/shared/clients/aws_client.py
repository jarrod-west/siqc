import boto3
from mypy_boto3_cloudformation.literals import CloudFormationServiceName
from mypy_boto3_connect.literals import ConnectServiceName
from typing import Any, Callable, cast


class AwsClient:
  """Generic AWS client, designed for other clients to inherit from."""

  def __init__(
    self, client_type: ConnectServiceName | CloudFormationServiceName
  ) -> None:
    """Constructor.

    Args:
        client_type (ConnectServiceName | CloudFormationServiceName): The underlying service type ("connect" or "cloudformation")
    """
    self.client = boto3.client(client_type)

  def _get_summary(
    self,
    list_function: str,
    top_level_key: str,
    match_key: str,
    match_values: str | list[str],
    filter_predicate: Callable[[Any], bool] = lambda x: True,
    paginate_args: dict[str, str | int] = {},
  ) -> Any:
    """General function to perform a "list" operation on an AWS resource and return all the responses.

    Args:
        list_function (str): The name of the function to call
        top_level_key (str): The response key that contains the resource summaries
        match_key (str): The key of a comparator used to filter the results
        match_values (str | list[str]): The value or values of the comparator used to filter the results
        filter_predicate (_type_, optional): Extra check to filter out responses. Defaults to lambda x:True.
        paginate_args (dict[str, str  |  int], optional): Arguments to parse to the paginator. Defaults to {}.

    Returns:
        Any: A list of the summary-type responses for the AWS resources that match the filter
    """
    # Handle array and singular matchers
    match_array = True if isinstance(match_values, list) else False

    if not match_array:
      match_values = cast(str, match_values)
      match_values = [match_values]

    # Return values for each requested item
    summaries = [None] * len(match_values)
    found = 0

    paginator = self.client.get_paginator(list_function)  # type: ignore[call-overload]
    for page in paginator.paginate(**paginate_args):
      for summary in page[top_level_key]:
        # Optional predicate to filter out results other than the name match
        if not filter_predicate(summary):
          continue

        try:
          index = match_values.index(summary[match_key])
          summaries[index] = summary
          found += 1

          # All values found, exit now
          if found == len(match_values):
            break
        except ValueError:
          pass

    return summaries if match_array else summaries[0]
