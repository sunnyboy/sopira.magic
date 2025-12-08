#..............................................................
#   ~/sopira.magic/version_01/sopira_magic/apps/m_factory/models.py
#   Factory Models - Company-owned entity
#..............................................................

"""
Factory Models.

Factory extends CompanyOwnedModel - inherits company FK automatically.
Scoping: User → Company → Factory
"""

from django.db import models
from django.utils.translation import gettext_lazy as _
from sopira_magic.apps.core.models import CompanyOwnedModel


class Factory(CompanyOwnedModel):
    """Factory - owned by Company."""
    
    address = models.CharField(
        max_length=255,
        blank=True,
        default="",
        help_text=_("Factory address")
    )
    
    class Meta(CompanyOwnedModel.Meta):
        verbose_name = _("Factory")
        verbose_name_plural = _("Factories")
        constraints = [
            models.UniqueConstraint(
                fields=["company", "code"],
                name="uq_factory_company_code",
            ),
            models.UniqueConstraint(
                fields=["human_id"],
                condition=models.Q(human_id__isnull=False),
                name="uq_factory_human_id",
            ),
        ]
