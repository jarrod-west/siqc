from pytest_mock import MockerFixture

from deploy import deploy
from deploy.setup import setup
from shared.test_helpers.helpers import MockConnectClient, not_raises
from shared.clients import connect_client


def test_setup(mocker: MockerFixture) -> None:
  mock_parameters = {
    "InstanceAlias": "alias",
    "PrivateNumber": "private",
    "PublicNumber": "public",
    "AgentUsername": "agent",
    "CustomerNumber": "customer",
    "DefaultRoutingProfile": "routing",
  }

  mock_client = MockConnectClient("alias")

  mocker.patch("dotenv.dotenv_values", return_value=mock_parameters)
  mocker.patch.object(deploy, "deploy", return_value=mock_parameters)
  mocker.patch.object(connect_client.ConnectClient, "__new__", return_value=mock_client)

  with not_raises():
    setup()
    assert mock_client.calls == [
      "__init__",
      "assign_contact_flow_number",
      "assign_user_to_routing_profile",
    ]
