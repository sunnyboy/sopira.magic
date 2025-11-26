#..............................................................
#   ~/sopira.magic/version_01/sopira_magic/apps/core/signals.py
#   Core Signals - Universal cross-database cascade delete
#   Handles cascade deletion across databases for all models
#..............................................................

"""
   Core Signals - Universal Cross-Database Cascade Delete.

   Django signals to handle proper cascade deletion across databases.
   Since Django's CASCADE doesn't work across databases, this signal
   automatically detects and deletes related records in other databases.

   How it works:
   1. On pre_delete signal, detects all ForeignKeys pointing to the deleted object
   2. For each ForeignKey, checks if related model is in different database
   3. If yes, deletes related records from that database before deletion

   Usage:
   Automatically registered for all models when core app is loaded.
   No manual registration needed.

   Important:
   - NO HARDCODING: This solution works universally for all models
   - Automatically detects cross-database relationships via db_router
   - Handles STATE → PRIMARY, LOGGING → PRIMARY, and any other cross-database relationships
"""

import logging
from django.db.models.signals import pre_delete
from django.dispatch import receiver
from django.apps import apps

logger = logging.getLogger(__name__)


@receiver(pre_delete)
def handle_cross_database_cascade(sender, instance, **kwargs):
    """
    Universal cross-database cascade delete handler.
    
    This signal automatically handles cascade deletion for ForeignKeys
    that span across databases (e.g., STATE → PRIMARY, LOGGING → PRIMARY).
    
    Args:
        sender: The model class being deleted
        instance: The model instance being deleted
        **kwargs: Additional signal arguments
    """
    try:
        from sopira_magic.db_router import DatabaseRouter
        
        router = DatabaseRouter()
        source_db = router.db_for_write(sender)
        
        # Get all models that might have ForeignKeys to this model
        for model in apps.get_models():
            # Skip if same model
            if model == sender:
                continue
            
            # Get all ForeignKey fields pointing to this model
            for field in model._meta.get_fields():
                if (hasattr(field, 'related_model') and 
                    field.related_model is not None and 
                    field.related_model == sender):
                    # Check if this is a cross-database relationship
                    target_db = router.db_for_write(model)
                    
                    if source_db != target_db:
                        # Cross-database ForeignKey detected
                        # Delete related records from target database
                        try:
                            # Get the field name
                            field_name = field.name
                            
                            # Build filter to find related records
                            filter_kwargs = {field_name: instance.id}
                            
                            # Delete related records from target database
                            related_count = model.objects.using(target_db).filter(**filter_kwargs).count()
                            
                            if related_count > 0:
                                model.objects.using(target_db).filter(**filter_kwargs).delete()
                                
                                logger.info(
                                    f"[CORE] Deleted {related_count} {model._meta.label} records "
                                    f"from {target_db} database for {sender._meta.label} (id={instance.id})"
                                )
                        except Exception as e:
                            # Log error but don't prevent deletion
                            # Target database might not exist or table might not exist yet
                            error_msg = str(e)
                            if 'does not exist' in error_msg.lower() or 'database' in error_msg.lower():
                                logger.debug(
                                    f"[CORE] Target database/tables not available for {model._meta.label}: {error_msg}"
                                )
                            else:
                                logger.warning(
                                    f"[CORE] Failed to delete {model._meta.label} records "
                                    f"from {target_db} database: {error_msg}"
                                )
                            
    except Exception as e:
        # Log error but don't prevent deletion
        logger.debug(f"[CORE] Cross-database cascade handler error: {str(e)}")

