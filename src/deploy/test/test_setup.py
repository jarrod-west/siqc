import dotenv
from typing import Any

from deploy import deploy
from deploy.setup import setup
from deploy.test.helpers import MockConnectClient
from shared.test.helpers import not_raises
from shared.clients import connect_client


def test_setup(monkeypatch: Any) -> None:
  with monkeypatch.context():
    mock_parameters = {
      "InstanceAlias": "alias",
      "PrivateNumber": "private",
      "PublicNumber": "public",
      "AgentUsername": "agent",
      "CustomerNumber": "customer",
      "DefaultRoutingProfile": "routing",
    }

    mock_client = MockConnectClient("alias")

    monkeypatch.setattr(dotenv, "dotenv_values", lambda: mock_parameters)
    monkeypatch.setattr(deploy, "deploy", lambda: {})
    monkeypatch.setattr(
      connect_client.ConnectClient, "__new__", lambda _x, _y: mock_client
    )

    with not_raises():
      setup()
      assert mock_client.calls == [
        "__init__",
        "assign_contact_flow_number",
        "assign_user_to_routing_profile",
      ]