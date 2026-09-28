"""Homelab fork: service calls go to the connection that reaches the
call's hub. With one local entry per hub, the services (registered by
whichever entry loads first) used to send every IR command to that first
hub - an IR command for another hub silently did nothing."""

from types import SimpleNamespace
from unittest.mock import MagicMock

import pytest
from homeassistant.exceptions import HomeAssistantError

from custom_components.lifesmart.const import DOMAIN
from custom_components.lifesmart.core.local_tcp_client import LifeSmartLocalTCPClient
from custom_components.lifesmart.services import LifeSmartServiceManager


def _local(node: str) -> MagicMock:
    client = MagicMock(spec=LifeSmartLocalTCPClient)
    client.node = node
    return client


def _manager(entries: dict, first_client) -> LifeSmartServiceManager:
    hass = SimpleNamespace(data={DOMAIN: entries} if entries is not None else {})
    return LifeSmartServiceManager(hass, first_client)


def test_each_hub_gets_its_own_local_connection():
    a, b, c = _local("HUB_A"), _local("HUB_B"), _local("HUB_C")
    manager = _manager({"e1": {"client": a}, "e2": {"client": b}, "e3": {"client": c}}, first_client=a)
    assert manager._client_for("HUB_B") is b
    assert manager._client_for("HUB_C") is c
    assert manager._client_for("HUB_A") is a


def test_a_cloud_connection_reaches_any_hub():
    cloud = MagicMock()  # not a local client
    manager = _manager({"cloud": {"client": cloud}}, first_client=cloud)
    assert manager._client_for("ANY_HUB") is cloud


def test_unknown_hub_with_only_local_connections_is_an_error():
    a = _local("HUB_A")
    manager = _manager({"e1": {"client": a}}, first_client=a)
    with pytest.raises(HomeAssistantError, match="HUB_Z"):
        manager._client_for("HUB_Z")


def test_no_entries_falls_back_to_the_registering_client():
    first = MagicMock()
    assert _manager(None, first_client=first)._client_for("HUB_A") is first
