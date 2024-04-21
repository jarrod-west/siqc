from mypy_boto3_connect.type_defs import (
  InstanceSummaryTypeDef,
  PhoneNumberSummaryTypeDef,
)
from typing import Any, Callable, cast

from src.shared.clients.aws_client import AwsClient


class ConnectClient(AwsClient):
  def __init__(self, instance_alias: str) -> None:
    super().__init__("connect")
    self.instance = cast(
      InstanceSummaryTypeDef,
      super()._get_summary(
        "list_instances", "InstanceSummaryList", "InstanceAlias", instance_alias
      ),
    )

  def _get_summary(
    self,
    list_function: str,
    top_level_key: str,
    match_key: str,
    match_values: str | list[str],
    filter_predicate: Callable[[Any], bool] = lambda x: True,
    paginate_args: dict[str, str | int] = {},
  ) -> Any:
    return super()._get_summary(
      list_function,
      top_level_key,
      match_key,
      match_values,
      filter_predicate,
      {"InstanceArn": self.instance["Arn"], **paginate_args},
    )

  def get_phone_number_summaries(
    self, phone_numbers: list[str]
  ) -> list[PhoneNumberSummaryTypeDef]:
    return cast(
      list[PhoneNumberSummaryTypeDef],
      self._get_summary(
        "list_phone_numbers_v2",
        "ListPhoneNumbersSummaryList",
        "PhoneNumber",
        phone_numbers,
      ),
    )
