#..............................................................
#   ~/sopira.magic/version_01/sopira_magic/apps/m_driver/models.py
#   Driver Models - Factory-scoped lookup entity
#..............................................................

"""
Driver Models.

Driver extends FactoryScopedModel - inherits factory FK automatically.
Scoping: User → Company → Factory → Driver
"""

from django.db import models
from django.utils.translation import gettext_lazy as _
from sopira_magic.apps.core.models import FactoryScopedModel


class Driver(FactoryScopedModel):
    """Driver - scoped to Factory."""
    
    avatar = models.ImageField(
        upload_to="drivers/%Y/%m/",
        blank=True,
        null=True,
        help_text=_("Driver avatar image")
    )
    
    class Meta(FactoryScopedModel.Meta):
        verbose_name = _("Driver")
        verbose_name_plural = _("Drivers")
        constraints = [
            models.UniqueConstraint(
                fields=["factory", "code"],
                name="uq_driver_factory_code",
            ),
        ]

