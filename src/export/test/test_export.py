import json
from pytest_mock import MockerFixture
from typing import cast

from export.export import export, export_flow
from shared.test_helpers.helpers import MockConnectClient
from shared.clients import connect_client


def test_export_flow(mocker: MockerFixture) -> None:
  mock_client = MockConnectClient("alias")
  mock_file = mocker.mock_open(read_data="open file")
  mocker.patch("builtins.open", mock_file)
  mocker.patch.object(connect_client.ConnectClient, "__new__", mock_client)

  mock_dump = mocker.patch.object(json, "dump")

  export_flow(
    cast(connect_client.ConnectClient, mock_client), "CallbackInbound", "flow arn"
  )

  assert mock_dump.called
  assert mock_dump.call_args == [
    ({"Message": "mock flow content"}, mock_file.return_value),
    {"indent": 2},
  ]
  assert mock_client.calls == ["__init__", "get_contact_flow"]


def test_export(mocker: MockerFixture) -> None:
  mock_client = MockConnectClient("alias")
  mock_file = mocker.mock_open(read_data="open file")
  mocker.patch("builtins.open", mock_file)
  mocker.patch.object(connect_client.ConnectClient, "__new__", return_value=mock_client)
  mock_dump = mocker.patch.object(json, "dump")
  mock_mkdir = mocker.patch("pathlib.Path.mkdir")

  mock_parameters = {
    "InstanceAlias": "alias",
    "PrivateNumber": "private",
    "PublicNumber": "public",
    "AgentUsername": "agent",
    "CustomerNumber": "customer",
    "DefaultRoutingProfile": "routing",
  }

  mocker.patch("dotenv.dotenv_values", return_value=mock_parameters)

  export()

  assert mock_mkdir.called
  assert mock_dump.call_args == [
    ({"Message": "mock flow content"}, mock_file.return_value),
    {"indent": 2},
  ]
  assert (
    mock_client.calls == ["__init__", "get_flow_summaries"] + ["get_contact_flow"] * 4
  )
