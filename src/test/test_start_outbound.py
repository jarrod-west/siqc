from pytest_mock import MockerFixture

from shared.test_helpers.helpers import MockConnectClient
from shared.clients import connect_client
from start_outbound import start_outbound


def test_start_outbound(mocker: MockerFixture) -> None:
  mock_parameters = {
    "InstanceAlias": "alias",
    "PrivateNumber": "private",
    "PublicNumber": "public",
    "AgentUsername": "agent",
    "CustomerNumber": "customer",
    "DefaultRoutingProfile": "routing",
  }

  mocker.patch("dotenv.dotenv_values", return_value=mock_parameters)
  mock_client = MockConnectClient("alias")
  mocker.patch.object(
    connect_client.ConnectClient, "__new__", lambda _x, _y: mock_client
  )

  start_outbound()

  assert mock_client.calls == ["__init__", "start_outbound"]
