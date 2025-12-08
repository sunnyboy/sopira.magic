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

# Single Source of Truth for relation configurations
RELATION_CONFIG = {
    # User O2M Company (One-to-Many: jeden user má viacero companies)
    'user_company': {
        'source': 'user.User',
        'target': 'company.Company',
        'type': 'ForeignKey',
        'field_name': 'user',
        'related_name': 'companies',
        'on_delete': 'PROTECT',
        'description': 'User owns multiple companies',
    },
    
    # Company O2M Factory (One-to-Many: jedna company má viacero factories)
    'company_factory': {
        'source': 'company.Company',
        'target': 'factory.Factory',
        'type': 'ForeignKey',
        'field_name': 'company',
        'related_name': 'factories',
        'on_delete': 'PROTECT',
        'description': 'Company owns multiple factories',
    },
    
    # Factory O2M ProductionLine (One-to-Many: jedna factory má viacero productionlines)
    'factory_productionline': {
        'source': 'factory.Factory',
        'target': 'productionline.ProductionLine',
        'type': 'ForeignKey',
        'field_name': 'factory',
        'related_name': 'production_lines',
        'on_delete': 'PROTECT',
        'description': 'Factory has multiple production lines',
    },
    
    # User O2M Photo (One-to-Many: user má viacero photos cez RelationInstance)
    'user_photo': {
        'source': 'user.User',
        'target': 'photo.Photo',
        'type': 'ForeignKey',
        'field_name': 'user',
        'related_name': 'photos',
        'on_delete': 'PROTECT',
        'description': 'User owns multiple photos',
    },
    
    # =====================================================================
    # Thermal Eye Relations (migrated from Thermal Eye)
    # =====================================================================
    
    # Factory O2M User (Factory.created_by - user who created the factory)
    'factory_user': {
        'source': 'm_user.User',
        'target': 'm_factory.Factory',
        'type': 'ForeignKey',
        'field_name': 'created_by',
        'related_name': 'factories',
        'on_delete': 'PROTECT',
        'description': 'User created multiple factories',
    },
    
    # Factory O2M Location (Factory has many locations)
    'location_factory': {
        'source': 'm_factory.Factory',
        'target': 'm_location.Location',
        'type': 'ForeignKey',
        'field_name': 'factory',
        'related_name': 'locations',
        'on_delete': 'PROTECT',
        'description': 'Factory has multiple locations',
    },
    
    # Factory O2M Carrier (Factory has many carriers)
    'carrier_factory': {
        'source': 'm_factory.Factory',
        'target': 'm_carrier.Carrier',
        'type': 'ForeignKey',
        'field_name': 'factory',
        'related_name': 'carriers',
        'on_delete': 'PROTECT',
        'description': 'Factory has multiple carriers',
    },
    
    # Factory O2M Driver (Factory has many drivers)
    'driver_factory': {
        'source': 'm_factory.Factory',
        'target': 'm_driver.Driver',
        'type': 'ForeignKey',
        'field_name': 'factory',
        'related_name': 'drivers',
        'on_delete': 'PROTECT',
        'description': 'Factory has multiple drivers',
    },
    
    # Factory O2M Pot (Factory has many pots)
    'pot_factory': {
        'source': 'm_factory.Factory',
        'target': 'm_pot.Pot',
        'type': 'ForeignKey',
        'field_name': 'factory',
        'related_name': 'pots',
        'on_delete': 'PROTECT',
        'description': 'Factory has multiple pots',
    },
    
    # Factory O2M Pit (Factory has many pits)
    'pit_factory': {
        'source': 'm_factory.Factory',
        'target': 'm_pit.Pit',
        'type': 'ForeignKey',
        'field_name': 'factory',
        'related_name': 'pits',
        'on_delete': 'PROTECT',
        'description': 'Factory has multiple pits',
    },
    
    # Location O2M Pit (Location has many pits)
    'pit_location': {
        'source': 'm_location.Location',
        'target': 'm_pit.Pit',
        'type': 'ForeignKey',
        'field_name': 'location',
        'related_name': 'pits',
        'on_delete': 'PROTECT',
        'description': 'Location has multiple pits',
        'nullable': True,
    },
    
    # Factory O2M Machine (Factory has many machines)
    'machine_factory': {
        'source': 'm_factory.Factory',
        'target': 'm_machine.Machine',
        'type': 'ForeignKey',
        'field_name': 'factory',
        'related_name': 'machines',
        'on_delete': 'PROTECT',
        'description': 'Factory has multiple machines',
    },
    
    # Factory O2M Camera (Factory has many cameras)
    'camera_factory': {
        'source': 'm_factory.Factory',
        'target': 'm_camera.Camera',
        'type': 'ForeignKey',
        'field_name': 'factory',
        'related_name': 'cameras',
        'on_delete': 'SET_NULL',
        'description': 'Factory has multiple cameras',
        'nullable': True,
    },
    
    # Location O2M Camera (Location has many cameras)
    'camera_location': {
        'source': 'm_location.Location',
        'target': 'm_camera.Camera',
        'type': 'ForeignKey',
        'field_name': 'location',
        'related_name': 'cameras',
        'on_delete': 'SET_NULL',
        'description': 'Location has multiple cameras',
        'nullable': True,
    },
    
    # Factory O2M Measurement (Factory has many measurements)
    'measurement_factory': {
        'source': 'm_factory.Factory',
        'target': 'm_measurement.Measurement',
        'type': 'ForeignKey',
        'field_name': 'factory',
        'related_name': 'measurements',
        'on_delete': 'PROTECT',
        'description': 'Factory has multiple measurements',
    },
    
    # Location O2M Measurement (Location has many measurements)
    'measurement_location': {
        'source': 'm_location.Location',
        'target': 'm_measurement.Measurement',
        'type': 'ForeignKey',
        'field_name': 'location',
        'related_name': 'measurements',
        'on_delete': 'PROTECT',
        'description': 'Location has multiple measurements',
    },
    
    # Carrier O2M Measurement (Carrier has many measurements)
    'measurement_carrier': {
        'source': 'm_carrier.Carrier',
        'target': 'm_measurement.Measurement',
        'type': 'ForeignKey',
        'field_name': 'carrier',
        'related_name': 'measurements',
        'on_delete': 'PROTECT',
        'description': 'Carrier has multiple measurements',
    },
    
    # Driver O2M Measurement (Driver has many measurements)
    'measurement_driver': {
        'source': 'm_driver.Driver',
        'target': 'm_measurement.Measurement',
        'type': 'ForeignKey',
        'field_name': 'driver',
        'related_name': 'measurements',
        'on_delete': 'PROTECT',
        'description': 'Driver has multiple measurements',
    },
    
    # Pot O2M Measurement (Pot has many measurements)
    'measurement_pot': {
        'source': 'm_pot.Pot',
        'target': 'm_measurement.Measurement',
        'type': 'ForeignKey',
        'field_name': 'pot',
        'related_name': 'measurements',
        'on_delete': 'PROTECT',
        'description': 'Pot has multiple measurements',
    },
    
    # Pit O2M Measurement (Pit has many measurements)
    'measurement_pit': {
        'source': 'm_pit.Pit',
        'target': 'm_measurement.Measurement',
        'type': 'ForeignKey',
        'field_name': 'pit',
        'related_name': 'measurements',
        'on_delete': 'PROTECT',
        'description': 'Pit has multiple measurements',
        'nullable': True,
    },
    
    # Machine O2M Measurement (Machine has many measurements)
    'measurement_machine': {
        'source': 'm_machine.Machine',
        'target': 'm_measurement.Measurement',
        'type': 'ForeignKey',
        'field_name': 'machine',
        'related_name': 'measurements',
        'on_delete': 'PROTECT',
        'description': 'Machine has multiple measurements',
        'nullable': True,
    },
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
