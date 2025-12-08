#..............................................................
#   ~/sopira.magic/version_01/sopira_magic/apps/m_pit/models.py
#   Pit Models - Factory-scoped with optional Location
#..............................................................

"""
Pit Models.

Pit extends FactoryScopedModel - inherits factory FK automatically.
Additional FK: location (optional)
Scoping: User → Company → Factory → Pit
"""

from django.db import models
from django.utils.translation import gettext_lazy as _
from sopira_magic.apps.core.models import FactoryScopedModel


class Pit(FactoryScopedModel):
    """Pit - scoped to Factory, optionally to Location."""
    
    location = models.ForeignKey(
        'location.Location',
        on_delete=models.PROTECT,
        related_name='pits',
        blank=True,
        null=True,
        help_text=_("Location within factory (optional)"),
    )
    
    capacity_tons = models.DecimalField(
        max_digits=8,
        decimal_places=3,
        blank=True,
        null=True,
        help_text=_("Kapacita jamy v tonách")
    )
    is_active = models.BooleanField(
        default=True,
        help_text=_("Je jama aktívna?")
    )
    
    class Meta(FactoryScopedModel.Meta):
        verbose_name = _("Pit")
        verbose_name_plural = _("Pits")
        indexes = [
            *FactoryScopedModel.Meta.indexes,
            models.Index(fields=["factory", "location"]),
        ]
        constraints = [
            models.UniqueConstraint(
                fields=["factory", "code"],
                name="uq_pit_factory_code",
            ),
        ]

