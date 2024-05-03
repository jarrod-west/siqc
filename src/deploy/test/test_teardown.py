import dotenv

from typing import Any

from deploy.teardown import teardown
from shared.test_helpers.helpers import MockConnectClient, not_raises
from shared.clients import connect_client


def test_teardown(monkeypatch: Any) -> None:
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
  monkeypatch.setattr(
    connect_client.ConnectClient, "__new__", lambda _x, _y: mock_client
  )

  with not_raises():
    teardown()
    assert mock_client.calls == [
      "__init__",
      "unassign_contact_flow_number",
      "assign_user_to_routing_profile",
    ]
