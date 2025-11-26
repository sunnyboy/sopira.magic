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
   - GENERATOR_CONFIG: Dictionary of model generation configurations
   - Each config has: model, count, fields, relations, post_create_hooks

   Field Generation Types:
   - template: Template-based generation (e.g., 'COMP-{index:03d}')
   - dataset: Use predefined dataset (e.g., 'business_name', 'first_name')
   - copy: Copy value from another field
   - lorem: Generate Lorem Ipsum text
   - random: Random value based on field type
   - static: Static value
   - increment: Incremental value
   - date_range: Random date within range
   - number_range: Random number within range

   Relation Types:
   - random: Each generated object gets a random related object from existing pool
     Example: 20 companies randomly assigned to 10 users (some users may have 0)
   - per_source: For each source object, generates N target objects (guaranteed coverage)
     Example: If 10 users exist and count_per_source=2, creates 20 companies (2 per user)
     Parameters:
       * type: 'per_source'
       * model: Source model path (e.g., 'user.User')
       * count_per_source: Number of target objects per source object (default: 1)
       * required: If True, creates source object if missing (default: False)
   - user: Uses provided user or first user for relation
     Example: All generated objects relate to the same user

   Configured Models:
   - company: Business name generation, relations to user
   - factory: Template-based names, relations to company
   - productionline: Template-based names, relations to factory
   - user: Full user generation with all fields (username, email, phone, address, role, etc.)

   Helper Functions:
   - get_generator_config(model_key): Get specific generator config
   - get_all_generator_configs(): Get all generator configurations

   Usage:
   ```python
   from sopira_magic.apps.generator.config import GENERATOR_CONFIG, get_generator_config
   config = get_generator_config('user')
   ```
"""

# Single Source of Truth for generator configurations
GENERATOR_CONFIG = {
    'company': {
        'model': 'company.Company',
        'count': 10,
        'fields': {
            'code': {
                'type': 'template',
                'template': 'COMP-{index:03d}',
            },
            'name': {
                'type': 'dataset',
                'dataset': 'business_name',
            },
            'human_id': {
                'type': 'copy',
                'from': 'code',
            },
            'comment': {
                'type': 'lorem',
                'words': 10,
            },
            'note': {
                'type': 'lorem',
                'words': 5,
            },
        },
        'relations': {
            'user': {
                'type': 'per_source',  # Changed from 'random' to 'per_source'
                'model': 'user.User',
                'count_per_source': 5,  # 5 companies per user (guaranteed)
                'required': True,
            },
        },
    },
    
    'factory': {
        'model': 'factory.Factory',
        'count': 20,
        'fields': {
            'code': {
                'type': 'template',
                'template': 'FAC-{index:03d}',
            },
            'name': {
                'type': 'template',
                'template': 'Factory {index}',
            },
            'human_id': {
                'type': 'copy',
                'from': 'code',
            },
            'comment': {
                'type': 'lorem',
                'words': 8,
            },
        },
        'relations': {
            'company': {
                'type': 'per_source',  # Changed from 'random' to 'per_source'
                'model': 'company.Company',
                'count_per_source': 3,  # 3 factories per company (guaranteed)
                'required': True,
            },
        },
    },
    
    'productionline': {
        'model': 'productionline.ProductionLine',
        'count': 50,
        'fields': {
            'code': {
                'type': 'template',
                'template': 'PL-{index:03d}',
            },
            'name': {
                'type': 'template',
                'template': 'Production Line {index}',
            },
            'human_id': {
                'type': 'copy',
                'from': 'code',
            },
        },
        'relations': {
            'factory': {
                'type': 'per_source',  # Changed from 'random' to 'per_source'
                'model': 'factory.Factory',
                'count_per_source': 4,  # 4 production lines per factory (guaranteed)
                'required': True,
            },
        },
    },
    
    'user': {
        'model': 'user.User',
        'count': 100,
        'fields': {
            'username': {
                'type': 'dataset',
                'dataset': 'username',
                # Will use first_name and last_name from context
            },
            'first_name': {
                'type': 'dataset',
                'dataset': 'first_name',
            },
            'last_name': {
                'type': 'dataset',
                'dataset': 'last_name',
            },
            'email': {
                'type': 'dataset',
                'dataset': 'email',
                # Will use first_name and last_name from context
            },
            'phone': {
                'type': 'dataset',
                'dataset': 'phone',
                'country': 'Slovakia',
            },
            'address': {
                'type': 'dataset',
                'dataset': 'address',
                'country': 'Slovakia',
            },
            'role': {
                'type': 'dataset',
                'dataset': 'role',
            },
            'date_of_birth': {
                'date_range': {
                    'start': '1950-01-01',
                    'end': '2005-12-31',
                },
            },
            'photo_url': {
                'type': 'dataset',
                'dataset': 'photo_url',
                # Will use full_name from context
            },
            'tags': {
                'type': 'dataset',
                'dataset': 'tags',
                'count': 3,  # Number of tags per user
                'as_list': True,  # Return as list for tag app
            },
            'is_active': {
                'type': 'static',
                'value': True,
            },
            'is_staff': {
                'type': 'static',
                'value': False,
            },
            'is_superuser': {
                'type': 'static',
                'value': False,
            },
        },
        # Note: tags will be handled separately via tag app (TaggedItem)
    },
    
    'photo': {
        'model': 'photo.Photo',
        'count': 200,
        'fields': {
            'code': {
                'type': 'template',
                'template': 'PHOTO-{index:03d}',
            },
            'name': {
                'type': 'template',
                'template': 'Photo {index}',
            },
            'human_id': {
                'type': 'copy',
                'from': 'code',
            },
            'photo_url': {
                'type': 'dataset',
                'dataset': 'photo_url',
            },
            'thumbnail_url': {
                'type': 'dataset',
                'dataset': 'thumbnail_url',
            },
            'width': {
                'number_range': {'min': 800, 'max': 1920},
                'step': 16,  # Round to multiples of 16 for better compression
            },
            'height': {
                'aspect_ratio': 16/9,  # Standard 16:9 aspect ratio (will use width from context)
            },
            'file_size': {
                'number_range': {'min': 100000, 'max': 5000000},
            },
        },
        'relations': {
            'user': {
                'type': 'per_source',  # Changed from 'random' to 'per_source'
                'model': 'user.User',
                'count_per_source': 20,  # 20 photos per user (guaranteed)
                'required': True,
            },
        },
    },
    
    # Example configs showing range support and new datasets:
    # 'example_with_ranges': {
    #     'model': 'example.Model',
    #     'fields': {
    #         'price': {
    #             'number_range': {'min': 10.0, 'max': 1000.0},
    #             'decimals': 2,
    #             'step': 0.5,
    #         },
    #         'quantity': {
    #             'number_range': {'min': 1, 'max': 100},
    #             'step': 1,
    #         },
    #         'created_date': {
    #             'date_range': {
    #                 'start': '2020-01-01',
    #                 'end': '2024-12-31',
    #             },
    #         },
    #         'work_time': {
    #             'time_range': {
    #                 'start': '08:00:00',
    #                 'end': '17:00:00',
    #             },
    #         },
    #         'email': {
    #             'type': 'dataset',
    #             'dataset': 'email',
    #             # Optional: 'first_name': 'John', 'last_name': 'Doe', 'domain': 'company.com'
    #         },
    #         'phone': {
    #             'type': 'dataset',
    #             'dataset': 'phone',
    #             # Optional: 'country': 'Slovakia'
    #         },
    #         'country': {
    #             'type': 'dataset',
    #             'dataset': 'country',
    #         },
    #         'city': {
    #             'type': 'dataset',
    #             'dataset': 'city',
    #         },
    #         'street': {
    #             'type': 'dataset',
    #             'dataset': 'street',
    #         },
    #         'postal_code': {
    #             'type': 'dataset',
    #             'dataset': 'postal_code',
    #             # Optional: 'country': 'Slovakia' (for country-specific format)
    #         },
    #         'address': {
    #             'type': 'dataset',
    #             'dataset': 'address',
    #             'as_dict': False,  # True for dict, False for string
    #             # Optional: 'country': 'Slovakia'
    #         },
    #     },
    # },
}


def get_generator_config(model_key: str) -> dict:
    """Get generator configuration by model key."""
    return GENERATOR_CONFIG.get(model_key, {})


def get_all_generator_configs() -> dict:
    """Get all generator configurations."""
    return GENERATOR_CONFIG.copy()
