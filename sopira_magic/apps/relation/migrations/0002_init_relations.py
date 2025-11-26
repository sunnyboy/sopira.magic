# Generated migration to initialize relations from config

from django.db import migrations


def init_relations_from_config(apps, schema_editor):
    """Initialize RelationRegistry from RELATION_CONFIG."""
    from django.core.management import call_command
    call_command('init_relations', verbosity=0)


def reverse_init_relations(apps, schema_editor):
    """Reverse migration - do nothing (relations can stay in DB)."""
    pass


class Migration(migrations.Migration):

    dependencies = [
        ('relation', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(
            init_relations_from_config,
            reverse_init_relations,
        ),
    ]

