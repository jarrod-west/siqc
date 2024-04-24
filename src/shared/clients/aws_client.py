import boto3
from mypy_boto3_cloudformation.literals import CloudFormationServiceName
from mypy_boto3_connect.literals import ConnectServiceName
from mypy_boto3_s3.literals import S3ServiceName
from typing import Any, Callable, cast


class AwsClient:
  def __init__(
    self,
    client_type: ConnectServiceName | CloudFormationServiceName | S3ServiceName,
  ) -> None:
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
