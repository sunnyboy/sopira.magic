#..............................................................
#   ~/sopira.magic/version_01/sopira_magic/apps/m_carrier/models.py
#   Carrier Models - Factory-scoped lookup entity
#..............................................................

"""
Carrier Models.

Carrier extends FactoryScopedModel - inherits factory FK automatically.
Scoping: User → Company → Factory → Carrier
"""

from django.db import models
from django.utils.translation import gettext_lazy as _
from sopira_magic.apps.core.models import FactoryScopedModel


class Carrier(FactoryScopedModel):
    """Carrier - scoped to Factory."""
    
    class Meta(FactoryScopedModel.Meta):
        verbose_name = _("Carrier")
        verbose_name_plural = _("Carriers")
        constraints = [
            models.UniqueConstraint(
                fields=["factory", "code"],
                name="uq_carrier_factory_code",
            ),
        ]

