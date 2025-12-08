"""Tests for security <-> scoping integration helpers."""

import sopira_magic.apps.security.integration.scoping as scoping_mod
from sopira_magic.apps.security.types import SecurityLevel, EnvironmentType


def test_get_effective_security_level_for_user_depends_on_role(monkeypatch):
    class DummyUser:
        pass

    user = DummyUser()

    # superuser -> STRICT
    monkeypatch.setattr(
        scoping_mod.scoping_registry,
        "get_scope_owner_role",
        lambda u: "superuser",
    )
    assert (
        scoping_mod.get_effective_security_level_for_user(user)
        is SecurityLevel.STRICT
    )

    # admin -> STRICT
    monkeypatch.setattr(
        scoping_mod.scoping_registry,
        "get_scope_owner_role",
        lambda u: "admin",
    )
    assert (
        scoping_mod.get_effective_security_level_for_user(user)
        is SecurityLevel.STRICT
    )

    # anything else -> STANDARD
    monkeypatch.setattr(
        scoping_mod.scoping_registry,
        "get_scope_owner_role",
        lambda u: "user",
    )
    assert (
        scoping_mod.get_effective_security_level_for_user(user)
        is SecurityLevel.STANDARD
    )


def test_is_request_allowed_for_scope_with_enum_and_string_and_invalid(monkeypatch):
    class DummyEngineEnum:
        @staticmethod
        def get_config(request):  # pragma: no cover - trivial
            return {
                "env_type": EnvironmentType.PRODUCTION,
                "security_level": SecurityLevel.MINIMAL,
            }

    class DummyEngineString:
        @staticmethod
        def get_config(request):  # pragma: no cover - trivial
            return {
                "env_type": EnvironmentType.PRODUCTION,
                "security_level": "strict",
            }

    class DummyEngineInvalid:
        @staticmethod
        def get_config(request):  # pragma: no cover - trivial
            return {
                "env_type": EnvironmentType.PRODUCTION,
                "security_level": "UNKNOWN",
            }

    # Enum value MINIMAL -> not allowed
    monkeypatch.setattr(scoping_mod, "SecurityEngine", DummyEngineEnum)
    assert scoping_mod.is_request_allowed_for_scope(None, object()) is False

    # String "strict" -> allowed
    monkeypatch.setattr(scoping_mod, "SecurityEngine", DummyEngineString)
    assert scoping_mod.is_request_allowed_for_scope(None, object()) is True

    # Invalid string -> coerced to STANDARD -> allowed
    monkeypatch.setattr(scoping_mod, "SecurityEngine", DummyEngineInvalid)
    assert scoping_mod.is_request_allowed_for_scope(None, object()) is True
