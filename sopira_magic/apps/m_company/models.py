#..............................................................
#   ~/sopira.magic/version_01/sopira_magic/apps/m_company/models.py
#   Company Models - Business entity model
#   Company with M2M relationship to User
#..............................................................

"""
   Company Models - Business Entity Model.

   Models:

1. Company (extends NamedWithCodeModel)
   - Business entity representing a company/organization
   - Inherits: id, uuid, created, updated, active, visible
   - Inherits: code, name, human_id, comment, note
   - M2M relationship with User via UserCompany

2. UserCompany (M2M join table)
   - Links User to Company with role
   - Allows user to belong to multiple companies
   - Supports company-level roles

   Usage:
   company = Company.objects.create(code='COMP-001', name='My Company')
    UserCompany.objects.create(user=user, company=company, role='admin')
"""

from django.conf import settings
from django.db import models
from django.utils.translation import gettext_lazy as _
from sopira_magic.apps.core.models import NamedWithCodeModel, TimeStampedModel


class Company(NamedWithCodeModel):
    """Company model - organization/business entity."""
    
    # M2M to User via UserCompany join table
    users = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        through='UserCompany',
        related_name='companies',
        blank=True,
    )
    
    class Meta(NamedWithCodeModel.Meta):
        verbose_name = _("Company")
        verbose_name_plural = _("Companies")


class UserCompany(TimeStampedModel):
    """M2M join table: User belongs to Company with role."""
    
    class CompanyRole(models.TextChoices):
        OWNER = 'owner', _('Owner')
        ADMIN = 'admin', _('Admin')
        MEMBER = 'member', _('Member')
        VIEWER = 'viewer', _('Viewer')
    
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='user_companies',
    )
    company = models.ForeignKey(
        Company,
        on_delete=models.CASCADE,
        related_name='company_users',
    )
    role = models.CharField(
        max_length=16,
        choices=CompanyRole.choices,
        default=CompanyRole.MEMBER,
        help_text=_('User role within this company'),
    )
    
    class Meta:
        verbose_name = _("User Company")
        verbose_name_plural = _("User Companies")
        unique_together = [['user', 'company']]
        indexes = [
            models.Index(fields=['user', 'company']),
        ]
    
    def __str__(self):
        return f"{self.user.username} @ {self.company.name} ({self.role})"
