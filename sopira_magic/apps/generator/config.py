#..............................................................
#   ~/sopira.magic/version_01/sopira_magic/apps/generator/config.py
#   Generator Config - SSOT for data generation
#   Single source of truth for all data generation rules
#..............................................................

"""
Generator Config - SSOT for Data Generation.

   Single source of truth for all data generation configurations.
   Defines how to generate data for each model with field-specific rules.

   Configuration Structure:
    GENERATOR_CONFIG = {
        'model_key': {
            'model': 'app_label.ModelName',      # Required
            'count': 10,                          # Default count
            'depends_on': ['other_model'],        # FK dependencies for ordering
            'fields': {...},                      # Field generation rules
            'relations': {...},                   # Dynamic relations (optional)
        },
    }

   Field Generation Types:
    - template: Template-based (e.g., 'COMP-{index:03d}')
    - dataset: Predefined dataset (e.g., 'business_name', 'first_name')
   - copy: Copy value from another field
   - lorem: Generate Lorem Ipsum text
   - random: Random value based on field type
   - static: Static value
   - increment: Incremental value
    - choice: Random choice from list
    - fk: ForeignKey field (NEW)

FK Field Type (for hardcoded ForeignKey):
    'field_name': {
        'type': 'fk',
        'model': 'app_label.ModelName',
        'strategy': 'random' | 'round_robin' | 'from_context',
        'nullable': True/False,  # Optional, default False
        'filter': {'field': 'value'},  # Optional queryset filter
    }

Relation Types (for dynamic relations via RelationService):
    - random: Each object gets random related object
    - per_source: For each source, generates N targets (guaranteed coverage)
    - user: Uses provided user or first user

Range Support:
    - date_range: {'start': '2024-01-01', 'end': '2024-12-31'}
    - time_range: {'start': '08:00:00', 'end': '17:00:00'}
    - number_range: {'min': 0, 'max': 100}
    - decimals: 2 (decimal places)
    - step: 5 (value increments)

   Helper Functions:
   - get_generator_config(model_key): Get specific generator config
   - get_all_generator_configs(): Get all generator configurations

   Usage:
   ```python
    from sopira_magic.apps.generator.config import get_generator_config
    config = get_generator_config('factory')
    
    # Or via management command:
    # python manage.py generate_all_data
    # python manage.py generate_data factory --count 10
   ```
"""

# =============================================================================
# GENERATOR_CONFIG - Single Source of Truth for data generation
# =============================================================================
#
# Generation Order (respects FK dependencies via 'depends_on'):
# 1. user (no dependencies)
# 2. company (no FK, but User M2M handled separately)
# 3. factory (company FK)
# 4. location, carrier, driver, pot, machine (factory FK)
# 5. pit (factory FK, location FK optional)
# 6. camera (factory FK, location FK optional)
# 7. measurement (factory, location, carrier, driver, pot, pit?, machine? FK)
# 8. photo, video (measurement FK)
#
# FK Field Type:
#   'field_name': {
#       'type': 'fk',
#       'model': 'app_label.ModelName',
#       'strategy': 'random' | 'round_robin' | 'from_context',
#       'filter': {'field': 'value'},  # optional queryset filter
#   }
# =============================================================================

GENERATOR_CONFIG = {
    # =========================================================================
    # LEVEL 0: No dependencies
    # =========================================================================
    
    'user': {
        'model': 'user.User',
        'count': 5,
        'depends_on': [],
        'fields': {
            'username': {'type': 'dataset', 'dataset': 'username'},
            'first_name': {'type': 'dataset', 'dataset': 'first_name'},
            'last_name': {'type': 'dataset', 'dataset': 'last_name'},
            'email': {'type': 'dataset', 'dataset': 'email'},
            'phone': {'type': 'dataset', 'dataset': 'phone', 'country': 'Slovakia'},
            'address': {'type': 'dataset', 'dataset': 'address', 'country': 'Slovakia'},
            'role': {'type': 'dataset', 'dataset': 'role'},
            'is_active': {'type': 'static', 'value': True},
            'is_staff': {'type': 'static', 'value': False},
            'is_superuser': {'type': 'static', 'value': False},
        },
    },
    
    # =========================================================================
    # LEVEL 1: No FK (User M2M handled via post_create hook)
    # =========================================================================
    
    'company': {
        'model': 'company.Company',
        'count': 3,
        'depends_on': ['user'],  # For M2M
        'fields': {
            'code': {'type': 'template', 'template': 'COMP-{index:03d}'},
            'name': {'type': 'dataset', 'dataset': 'business_name'},
            'human_id': {'type': 'copy', 'from': 'code'},
            'comment': {'type': 'lorem', 'words': 10},
            'note': {'type': 'lorem', 'words': 5},
            },
        },
    
    # =========================================================================
    # LEVEL 2: Company FK
    # =========================================================================
    
    'factory': {
        'model': 'factory.Factory',
        'count': 6,
        'depends_on': ['company'],
        'fields': {
            'code': {'type': 'template', 'template': 'FAC-{index:03d}'},
            'name': {'type': 'template', 'template': 'Factory {index}'},
            'human_id': {'type': 'copy', 'from': 'code'},
            'address': {'type': 'dataset', 'dataset': 'address', 'country': 'Slovakia'},
            'comment': {'type': 'lorem', 'words': 8},
            # FK field
            'company': {
                'type': 'fk',
                'model': 'company.Company',
                'strategy': 'round_robin',
            },
        },
    },
    
    # =========================================================================
    # LEVEL 3: Factory FK (lookup entities)
    # =========================================================================
    
    'location': {
        'model': 'location.Location',
        'count': 12,
        'depends_on': ['factory'],
        'fields': {
            'code': {'type': 'template', 'template': 'LOC-{index:03d}'},
            'name': {'type': 'dataset', 'dataset': 'working_place'},
            'human_id': {'type': 'copy', 'from': 'code'},
            'factory': {
                'type': 'fk',
                'model': 'factory.Factory',
                'strategy': 'round_robin',
            },
        },
    },
    
    'carrier': {
        'model': 'carrier.Carrier',
        'count': 12,
        'depends_on': ['factory'],
        'fields': {
            'code': {'type': 'template', 'template': 'CAR-{index:03d}'},
            'name': {'type': 'template', 'template': 'Carrier {index}'},
            'human_id': {'type': 'copy', 'from': 'code'},
            'factory': {
                'type': 'fk',
                'model': 'factory.Factory',
                'strategy': 'round_robin',
            },
        },
    },
    
    'driver': {
        'model': 'driver.Driver',
        'count': 18,
        'depends_on': ['factory'],
        'fields': {
            'code': {'type': 'template', 'template': 'DRV-{index:03d}'},
            'name': {'type': 'dataset', 'dataset': 'full_name'},
            'human_id': {'type': 'copy', 'from': 'code'},
            'factory': {
                'type': 'fk',
                'model': 'factory.Factory',
                'strategy': 'round_robin',
            },
        },
    },
    
    'pot': {
        'model': 'pot.Pot',
        'count': 24,
        'depends_on': ['factory'],
        'fields': {
            'code': {'type': 'template', 'template': 'POT-{index:03d}'},
            'name': {'type': 'template', 'template': 'Pot {index}'},
            'human_id': {'type': 'copy', 'from': 'code'},
            'knocks_max': {'number_range': {'min': 15, 'max': 25}},
            'weight_nominal_kg': {'number_range': {'min': 500.0, 'max': 2000.0}, 'decimals': 2},
            'factory': {
                'type': 'fk',
                'model': 'factory.Factory',
                'strategy': 'round_robin',
            },
        },
    },
    
    'pit': {
        'model': 'pit.Pit',
        'count': 12,
        'depends_on': ['factory', 'location'],
        'fields': {
            'code': {'type': 'template', 'template': 'PIT-{index:03d}'},
            'name': {'type': 'template', 'template': 'Pit {index}'},
            'human_id': {'type': 'copy', 'from': 'code'},
            'capacity_tons': {'number_range': {'min': 50.0, 'max': 500.0}, 'decimals': 2},
            'is_active': {'type': 'static', 'value': True},
            'factory': {
                'type': 'fk',
                'model': 'factory.Factory',
                'strategy': 'round_robin',
            },
            'location': {
                'type': 'fk',
                'model': 'location.Location',
                'strategy': 'random',
                'nullable': True,  # Optional FK
            },
        },
    },
    
    'machine': {
        'model': 'machine.Machine',
        'count': 6,
        'depends_on': ['factory'],
        'fields': {
            'code': {'type': 'template', 'template': 'MACH-{index:03d}'},
            'name': {'type': 'dataset', 'dataset': 'equipment'},
            'human_id': {'type': 'copy', 'from': 'code'},
            'firmware_number': {'type': 'template', 'template': 'FW-{index}.0.0'},
            'factory': {
                'type': 'fk',
                'model': 'factory.Factory',
                'strategy': 'round_robin',
            },
        },
    },
    
    'camera': {
        'model': 'camera.Camera',
        'count': 12,
        'depends_on': ['factory', 'location'],
        'fields': {
            'code': {'type': 'template', 'template': 'CAM-{index:03d}'},
            'name': {'type': 'template', 'template': 'Thermal Camera {index}'},
            'human_id': {'type': 'copy', 'from': 'code'},
            'manufacturer': {'type': 'static', 'value': 'FLIR'},
            'manufacturer_name': {'type': 'static', 'value': 'FLIR Systems'},
            'camera_serie': {'type': 'template', 'template': 'A{index}00'},
            'camera_sn': {'type': 'template', 'template': 'SN{index:08d}'},
            'ip': {'type': 'template', 'template': '192.168.1.{index}'},
            'port': {'type': 'static', 'value': 8080},
            'protocol': {'type': 'static', 'value': 'RTSP'},
            'resolution': {'type': 'static', 'value': '640x480'},
            'factory': {
                'type': 'fk',
                'model': 'factory.Factory',
                'strategy': 'round_robin',
            },
            'location': {
                'type': 'fk',
                'model': 'location.Location',
                'strategy': 'random',
                'nullable': True,
            },
        },
    },
    
    # =========================================================================
    # LEVEL 4: Complex FK (Measurement)
    # =========================================================================
    
    'measurement': {
        'model': 'measurement.Measurement',
        'count': 50,
        'depends_on': ['factory', 'location', 'carrier', 'driver', 'pot', 'pit', 'machine'],
        'fields': {
            'dump_date': {'date_range': {'start': '2024-01-01', 'end': '2024-12-31'}},
            'dump_time': {'time_range': {'start': '06:00:00', 'end': '22:00:00'}},
            'pit_number': {'type': 'template', 'template': 'P{index}'},
            'pot_side': {'type': 'choice', 'choices': ['FRONT', 'BACK', 'NONE']},
            'pot_knocks': {'number_range': {'min': 5, 'max': 25}},
            'pot_weight_kg': {'number_range': {'min': 800.0, 'max': 1800.0}, 'decimals': 3},
            'roi_temp_max_c': {'number_range': {'min': 800.0, 'max': 1200.0}, 'decimals': 2},
            'roi_temp_mean_c': {'number_range': {'min': 700.0, 'max': 1000.0}, 'decimals': 2},
            'roi_temp_min_c': {'number_range': {'min': 500.0, 'max': 800.0}, 'decimals': 2},
            'comment': {'type': 'lorem', 'words': 5},
            # FK fields
            'factory': {
                'type': 'fk',
                'model': 'factory.Factory',
                'strategy': 'random',
            },
            'location': {
                'type': 'fk',
                'model': 'location.Location',
                'strategy': 'random',
            },
            'carrier': {
                'type': 'fk',
                'model': 'carrier.Carrier',
                'strategy': 'random',
            },
            'driver': {
                'type': 'fk',
                'model': 'driver.Driver',
                'strategy': 'random',
            },
            'pot': {
                'type': 'fk',
                'model': 'pot.Pot',
                'strategy': 'random',
            },
            'pit': {
                'type': 'fk',
                'model': 'pit.Pit',
                'strategy': 'random',
                'nullable': True,
            },
            'machine': {
                'type': 'fk',
                'model': 'machine.Machine',
                'strategy': 'random',
                'nullable': True,
            },
        },
    },
    
    # =========================================================================
    # LEVEL 5: Measurement FK (Media)
    # =========================================================================
    
    'photo': {
        'model': 'photo.Photo',
        'count': 100,
        'depends_on': ['measurement'],
        'fields': {
            'photo_url': {'type': 'dataset', 'dataset': 'photo_url'},
            'thumbnail_url': {'type': 'dataset', 'dataset': 'thumbnail_url'},
            'width': {'number_range': {'min': 640, 'max': 1920}, 'step': 16},
            'height': {'number_range': {'min': 480, 'max': 1080}, 'step': 16},
            'file_size': {'number_range': {'min': 100000, 'max': 5000000}},
            'measurement': {
                'type': 'fk',
                'model': 'measurement.Measurement',
                'strategy': 'round_robin',
            },
        },
    },
    
    'video': {
        'model': 'video.Video',
        'count': 50,
        'depends_on': ['measurement'],
        'fields': {
            'video_url': {'type': 'template', 'template': 'https://videos.example.com/video_{index}.mp4'},
            'thumbnail_url': {'type': 'dataset', 'dataset': 'thumbnail_url'},
            'duration': {'number_range': {'min': 5, 'max': 120}},
            'file_size': {'number_range': {'min': 1000000, 'max': 50000000}},
            'measurement': {
                'type': 'fk',
                'model': 'measurement.Measurement',
                'strategy': 'round_robin',
            },
        },
    },
}


def get_generator_config(model_key: str) -> dict:
    """Get generator configuration by model key."""
    return GENERATOR_CONFIG.get(model_key, {})


def get_all_generator_configs() -> dict:
    """Get all generator configurations."""
    return GENERATOR_CONFIG.copy()
