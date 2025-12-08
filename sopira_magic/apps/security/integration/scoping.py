"""Integration helpers medzi security modulom a scoping engine.

Prvá verzia obsahuje len jednoduché helper funkcie bez zásahov
do interného kódu scoping enginu.
"""

from typing import Any

from sopira_magic.apps.scoping import registry as scoping_registry

from ..engine import SecurityEngine
from ..types import SecurityLevel


def get_effective_security_level_for_user(user: Any) -> SecurityLevel:
    """Vypočítaj efektívny SecurityLevel pre daného usera.

    Môže byť použitý v budúcich pravidlách scoping enginu alebo auditoch.
    Aktuálna implementácia je konzervatívna a iba mapuje role
    na úroveň bezpečnosti.
    """

    role = scoping_registry.get_scope_owner_role(user)

    if role == "superuser":
        return SecurityLevel.STRICT
    if role == "admin":
        return SecurityLevel.STRICT

    return SecurityLevel.STANDARD


def is_request_allowed_for_scope(request, scope_owner: Any) -> bool:
    """Príklad helpera: skombinuj security level a scoping rolu.

    Zatiaľ iba overí, či je security level minimálne STANDARD
    pre bežné požiadavky. Môže byť rozšírené o ďalšie pravidlá.
    """

    cfg = SecurityEngine.get_config(request)
    current_level = cfg["security_level"]

    if isinstance(current_level, SecurityLevel):
        return current_level in {SecurityLevel.STANDARD, SecurityLevel.STRICT, SecurityLevel.PARANOID}

    try:
        current_level_enum = SecurityLevel(str(current_level))
    except ValueError:
        current_level_enum = SecurityLevel.STANDARD

    return current_level_enum in {
        SecurityLevel.STANDARD,
        SecurityLevel.STRICT,
        SecurityLevel.PARANOID,
    }
