#..............................................................
#   ~/sopira.magic/version_01/sopira_magic/apps/internationalization/models.py
#   Internationalization Models - Translation system
#   Multi-language translation management
#..............................................................

"""
   Internationalization Models - Translation System.

   Models for managing translations and internationalization.
   Supports multiple languages and translation contexts.

   Models:

   Translation (extends TimeStampedModel)
   - Translation entry model
   - Fields: key, language, value, context
   - Unique constraint: key + language + context
   - Indexed on: language + key
   - Language codes: en, sk, de, etc.
   - Stores translations for different languages and contexts

   Usage:
   ```python
   from sopira_magic.apps.internationalization.models import Translation
   translation = Translation.objects.create(
       key='welcome.message',
       language='sk',
       value='Vitajte',
       context='ui'
   )
   ```
"""

from django.db import models
from django.utils.translation import gettext_lazy as _
from sopira_magic.apps.core.models import TimeStampedModel


class Translation(TimeStampedModel):
    """Translation model."""
    key = models.CharField(max_length=512, db_index=True)
    language = models.CharField(max_length=10, db_index=True)  # en, sk, de, etc.
    value = models.TextField()
    context = models.CharField(max_length=255, blank=True, default="")
    
    class Meta:
        verbose_name = _("Translation")
        verbose_name_plural = _("Translations")
        unique_together = [['key', 'language', 'context']]
        indexes = [
            models.Index(fields=['language', 'key']),
        ]
