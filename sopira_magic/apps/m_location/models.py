#..............................................................
#   ~/sopira.magic/version_01/sopira_magic/apps/m_location/models.py
#   Location Models - Factory-scoped lookup entity
#..............................................................

"""
Location Models.

Location extends FactoryScopedModel - inherits factory FK automatically.
Scoping: User → Company → Factory → Location
"""

from django.db import models
from django.utils.translation import gettext_lazy as _
from sopira_magic.apps.core.models import FactoryScopedModel


class Location(FactoryScopedModel):
    """Location - scoped to Factory."""
    
    class Meta(FactoryScopedModel.Meta):
        verbose_name = _("Location")
        verbose_name_plural = _("Locations")
        constraints = [
            models.UniqueConstraint(
                fields=["factory", "code"],
                name="uq_location_factory_code",
            ),
        ]

