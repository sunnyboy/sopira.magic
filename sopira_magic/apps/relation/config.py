#..............................................................
#   ~/sopira.magic/version_01/sopira_magic/apps/relation/config.py
#   Relation Config - SSOT for relation definitions
#   Single source of truth for all model relations
#..............................................................

"""
Relation Config - SSOT for Relation Definitions.

   Single source of truth for all relation definitions in the project.
   All relations are defined here, not hardcoded in models.

   Configuration Structure:
   - RELATION_CONFIG: Dictionary of relation definitions
   - Each relation has: source, target, type, field_name, related_name, on_delete, description

   Defined Relations:
   - user_company: User O2M Company (one user has many companies)
   - company_factory: Company O2M Factory (one company has many factories)
   - factory_productionline: Factory O2M ProductionLine (one factory has many production lines)
   - user_photo: User O2M Photo (one user has many photos)

   Helper Functions:
   - get_relation_config(relation_key): Get specific relation config
   - get_relations_for_source(source_model): Get all relations where model is source
   - get_relations_for_target(target_model): Get all relations where model is target
   - get_all_relations(): Get all relation configurations

   Usage:
   ```python
   from sopira_magic.apps.relation.config import RELATION_CONFIG, get_relation_config
   config = get_relation_config('user_company')
   ```
"""

# =====================================================================
# Config-driven Relations (SSOT)
# =====================================================================
# Pre performance používame hardcoded FK/M2M v modeloch kde je to možné.
# Config-driven relations (RelationInstance) sa používajú len pre:
# - Photo/Video relationships (dynamické, bez hardcoded FK)
# - Budúce M2M relationships ktoré nemajú hardcoded ekvivalent
#
# REMOVED (duplicitné - existujú hardcoded FK/M2M):
# - user_company (UserCompany M2M)
# - company_factory (Factory.company FK)
# - location_factory (Location.factory FK)
# - carrier_factory (Carrier.factory FK)
# - driver_factory (Driver.factory FK)
# - pot_factory (Pot.factory FK)
# - pit_factory (Pit.factory FK)
# - pit_location (Pit.location FK)
# - machine_factory (Machine.factory FK)
# - camera_factory (Camera.factory FK)
# - camera_location (Camera.location FK)
# - measurement_* (všetky Measurement FK)
# - factory_user (deprecated created_by FK)
# - factory_productionline (hardcoded FK)
# =====================================================================

RELATION_CONFIG = {
    # User O2M Photo (One-to-Many: user má viacero photos cez RelationInstance)
    # Config-driven - BEZ hardcoded FK
    'user_photo': {
        'source': 'user.User',
        'target': 'photo.Photo',
        'type': 'ForeignKey',
        'field_name': 'user',
        'related_name': 'photos',
        'on_delete': 'PROTECT',
        'description': 'User owns multiple photos',
    },
    
    # TODO: Pridať user_video ak existuje Video model
}


def get_relation_config(relation_key: str) -> dict:
    """Get relation configuration by key."""
    return RELATION_CONFIG.get(relation_key, {})


def get_relations_for_source(source_model: str) -> list:
    """Get all relations where source_model is the source."""
    return [
        config for key, config in RELATION_CONFIG.items()
        if config.get('source') == source_model
    ]


def get_relations_for_target(target_model: str) -> list:
    """Get all relations where target_model is the target."""
    return [
        config for key, config in RELATION_CONFIG.items()
        if config.get('target') == target_model
    ]


def get_all_relations() -> dict:
    """Get all relation configurations."""
    return RELATION_CONFIG.copy()
