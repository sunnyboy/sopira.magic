#..............................................................
#   ~/sopira.magic/version_01/sopira_magic/apps/m_machine/models.py
#   Machine Models - Factory-scoped entity
#..............................................................

"""
Machine Models.

Machine extends FactoryScopedModel - inherits factory FK automatically.
Scoping: User → Company → Factory → Machine
"""

import uuid
from django.db import models
from django.utils.translation import gettext_lazy as _
from sopira_magic.apps.core.models import FactoryScopedModel


class Machine(FactoryScopedModel):
    """Machine - scoped to Factory."""
    
    machine_uuid = models.UUIDField(
        unique=True,
        db_index=True,
        default=uuid.uuid4,
        help_text=_("Jedinečné UUID kamery/zariadenia")
    )
    firmware_number = models.CharField(
        max_length=100,
        blank=True,
        default="",
        help_text=_("Číslo firmware")
    )
    
    config_hardware = models.JSONField(blank=True, null=True)
    config_software = models.JSONField(blank=True, null=True)
    machine_log = models.JSONField(blank=True, null=True)
    machine_state = models.JSONField(blank=True, null=True)
    
    class Meta(FactoryScopedModel.Meta):
        verbose_name = _("Machine")
        verbose_name_plural = _("Machines")
        indexes = [
            *FactoryScopedModel.Meta.indexes,
            models.Index(fields=["machine_uuid"]),
        ]
        constraints = [
            models.UniqueConstraint(
                fields=["factory", "code"],
                name="uq_machine_factory_code",
            ),
        ]

