#..............................................................
#   ~/sopira.magic/version_01/sopira_magic/apps/m_pot/models.py
#   Pot Models - Factory-scoped lookup entity       
#..............................................................

"""
Pot Models.

Pot extends FactoryScopedModel - inherits factory FK automatically.
Scoping: User → Company → Factory → Pot
"""

from django.core.validators import MaxValueValidator
from django.db import models
from django.utils.translation import gettext_lazy as _
from sopira_magic.apps.core.models import FactoryScopedModel


class Pot(FactoryScopedModel):
    """Pot - scoped to Factory."""
    
    knocks_max = models.PositiveIntegerField(
        default=25,
        validators=[MaxValueValidator(25)],
        help_text=_("Max. počet úderov/ťuknutí pre tento kotol (0..25)")
    )
    weight_nominal_kg = models.DecimalField(
        max_digits=8,
        decimal_places=3,
        blank=True,
        null=True,
        help_text=_("Voliteľná nominálna hmotnosť kotla (kg)")
    )
    
    class Meta(FactoryScopedModel.Meta):
        verbose_name = _("Pot")
        verbose_name_plural = _("Pots")
        constraints = [
            models.UniqueConstraint(
                fields=["factory", "code"],
                name="uq_pot_factory_code",
            ),
        ]

