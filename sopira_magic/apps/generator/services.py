#..............................................................
#   ~/sopira.magic/version_01/sopira_magic/apps/generator/services.py
#   GeneratorService - Universal data generation service
#   SSOT, config-driven, universal data generator for any model
#..............................................................

"""
GeneratorService - Universal Data Generation Service.

   This module provides a universal, config-driven data generation service that can create
   synthetic data for any Django model based on centralized configuration (SSOT).

   Key Features:
   - Config-Driven: All generation rules defined in `config.py` (SSOT)
   - Universal: Works with any Django model, auto-detects field types
   - Dependency Resolution: Automatically handles model dependencies and generation order
   - Relation Support: Creates dynamic relations via `relation` app
   - Post-Creation Hooks: Supports custom actions after object creation (e.g., UserPreference, Tags)
   - Transaction Safety: All operations wrapped in database transactions

   Core Components:

   1. GeneratorService.generate_data()
      - Generates data for a specific model based on config key
      - Supports field type auto-detection (CharField, IntegerField, DateField, etc.)
      - Handles field dependencies (e.g., email generated from first_name + last_name)
      - Creates relations via RelationService
      - Executes post_create_hooks (UserPreference, Tags, etc.)
      - Supports two relation generation modes:
        * 'random': Each generated object gets a random related object (default)
        * 'per_source': For each source object, generates N target objects (guaranteed coverage)

   2. GeneratorService.generate_seed_data()
      - Generates seed data for all configured models
      - Builds dependency graph and generates in topological order
      - Ensures related objects exist before creating relations

   3. GeneratorService.clear_data()
      - Clears generated data while optionally preserving oldest records
      - Useful for testing and data refresh scenarios

   Configuration Flow:
   1. `config.py` defines GENERATOR_CONFIG (SSOT) with field generation rules
   2. `datasets.py` provides data pools (names, addresses, business names, etc.)
   3. `field_generators.py` handles field type detection and value generation
   4. `services.py` orchestrates the generation process

   Usage Example:
   ```python
   # Generate 100 users
   users = GeneratorService.generate_data('user', count=100)

   # Generate all seed data respecting dependencies
   counts = GeneratorService.generate_seed_data()

   # Generate companies with per_source relation (2 companies per user)
   # Config: relations={'user': {'type': 'per_source', 'count_per_source': 2}}
   companies = GeneratorService.generate_data('company')
   # Result: If 10 users exist, creates 20 companies (2 per user)
   ```

   Integration:
   - Uses `relation` app for dynamic relationship creation
   - Uses `tag` app for tagging generated objects
   - Respects model field types and constraints
   - Handles User model password hashing specially
"""

import random
from typing import Dict, Any, List, Optional
from django.db import transaction
from django.apps import apps
from django.db import models
import time

from .config import get_generator_config, get_all_generator_configs
from .field_generators import generate_field_value
from .datasets import generate_tags
from sopira_magic.apps.relation.services import RelationService
from .progress import ProgressTracker
from .progress_state import is_cancel_requested


class GeneratorService:
    """Universal service for generating data for any model based on config."""
    
    @staticmethod
    def get_model_class(model_path: str):
        """Get model class from model path (e.g., 'company.Company')."""
        app_label, model_name = model_path.split('.')
        return apps.get_model(app_label, model_name)
    
    @staticmethod
    def generate_data(model_key: str, count: Optional[int] = None, user=None, progress: ProgressTracker = None, job_id: str = None) -> List[Any]:
        """
        Generate data for a model based on config.
        
        This method supports two generation modes:
        1. Standard mode: Generates N objects with random relations (if configured)
        2. Per-source mode: If any relation has type='per_source', generates N objects
           for each source object, ensuring guaranteed coverage.
        
        Args:
            model_key: Key from GENERATOR_CONFIG (e.g., 'company', 'factory')
            count: Number of records to generate (overrides config count)
                   Note: For 'per_source' relations, this parameter is ignored and
                   the count is calculated as: source_count * count_per_source
            user: User instance for relations (optional, used for 'user' relation type)
        
        Returns:
            List of created model instances
        
        Relation Types:
            - 'random': Each generated object gets a random related object from existing pool
            - 'per_source': For each source object, generates N target objects (count_per_source)
              Example: If 10 users exist and count_per_source=2, creates 20 companies (2 per user)
            - 'user': Uses provided user or first user for relation
        
        Example:
            ```python
            # Standard generation (random relations)
            companies = GeneratorService.generate_data('company', count=20)
            # Creates 20 companies, each randomly assigned to a user
            
            # Per-source generation (guaranteed coverage)
            # Config: relations={'user': {'type': 'per_source', 'count_per_source': 2}}
            companies = GeneratorService.generate_data('company')
            # If 10 users exist, creates 20 companies (2 per user, guaranteed)
            ```
        """
        import logging
        logger = logging.getLogger(__name__)
        
        logger.info(f"[GENERATOR] generate_data START: model_key={model_key}, count={count}")
        
        config = get_generator_config(model_key)
        if not config:
            raise ValueError(f"Generator config '{model_key}' not found")
        
        model_path = config['model']
        model_class = GeneratorService.get_model_class(model_path)
        
        existing_count_before = model_class.objects.count()
        logger.info(f"[GENERATOR] Model: {model_path}, existing objects before: {existing_count_before}")
        
        # Check if any relation uses 'per_source' type
        relations_config = config.get('relations', {})
        has_per_source = any(
            rel_config.get('type') == 'per_source'
            for rel_config in relations_config.values()
        )
        
        # If per_source relation exists, use special generation strategy
        if has_per_source:
            logger.info(f"[GENERATOR] Detected per_source relation, delegating to _generate_data_per_source")
            result = GeneratorService._generate_data_per_source(
                model_key, config, relations_config, user
            )
            existing_count_after = model_class.objects.count()
            logger.info(f"[GENERATOR] generate_data COMPLETE: model_key={model_key}, created={len(result)}, total_in_db={existing_count_after}")
            return result
        
        # Standard generation mode
        logger.info(f"[GENERATOR] Using standard generation mode")
        target_count = count or config.get('count', 10)
        logger.info(f"[GENERATOR] Target count: {target_count}")
        
        created_objects = []
        existing_count = model_class.objects.count()
        
        # Precompute password hash once for user generation to avoid repeated hashing (perf)
        hashed_user_password = None
        if model_path == "user.User":
            from django.contrib.auth.hashers import make_password
            hashed_user_password = make_password("password123")

        start_time = time.time()

        # Logging cadence: factories sú pomalé, loguj každých 5; inak každých 500
        log_every = 5 if model_key == "factory" else 500

        for i in range(1, target_count + 1):
            if job_id and is_cancel_requested(job_id):
                logger.info(f"[GENERATOR] Cancel requested, stopping model {model_key}")
                break
            index = existing_count + i
            context = {}
            
            # Generate field values
            field_values = {}
            fields_config = config.get('fields', {})
            
            for field_name, field_config in fields_config.items():
                try:
                    field = model_class._meta.get_field(field_name)
                    value = generate_field_value(field, field_config, index, context)
                    field_values[field_name] = value
                    context[field_name] = value  # Add to context for dependent fields
                except Exception as e:
                    # Skip fields that don't exist or can't be generated
                    logger.debug(f"[GENERATOR] Skipping field {field_name}: {str(e)}")
                    continue
            
            # Create object (per-object transaction to allow recovery from errors)
            try:
                with transaction.atomic():
                    # Special handling for User model (password required)
                    if model_path == 'user.User':
                        # Use precomputed hash to speed up bulk user generation
                        if 'password' not in field_values:
                            field_values['password'] = hashed_user_password
                        obj = model_class.objects.create(**field_values)
                    else:
                        obj = model_class.objects.create(**field_values)
                
                created_objects.append(obj)
                if progress:
                    progress.step(1, note=model_key)
                
                # Handle tags if tag app is available
                if 'tags' in config.get('fields', {}):
                    tags_config = config['fields']['tags']
                    if tags_config.get('type') == 'dataset':
                        tags = generate_tags(tags_config.get('count'))
                        # Add tags via tag app if available
                        try:
                            from sopira_magic.apps.m_tag.models import Tag, TaggedItem
                            from django.contrib.contenttypes.models import ContentType
                            for tag_name in tags:
                                tag, _ = Tag.objects.get_or_create(name=tag_name)
                                TaggedItem.objects.get_or_create(
                                    tag=tag,
                                    content_type=ContentType.objects.get_for_model(obj.__class__),
                                    object_id=obj.id
                                )
                        except Exception:
                            pass  # Tag app might not be ready
                
                # Handle relations
                for relation_field, relation_config in relations_config.items():
                    GeneratorService._create_relation(
                        obj, relation_field, relation_config, model_key, user
                    )
                
            except Exception as e:
                # Skip objects that can't be created
                logger.error(f"[GENERATOR] Failed to create object {i}/{target_count}: {str(e)}")
                continue
        
        existing_count_after = model_class.objects.count()
        elapsed = time.time() - start_time
        logger.info(f"[GENERATOR] generate_data COMPLETE: model_key={model_key}, created={len(created_objects)}, expected={target_count}, total_in_db={existing_count_after}, elapsed={elapsed:.2f}s")
        return created_objects
    
    @staticmethod
    def _generate_data_per_source(
        model_key: str,
        config: Dict[str, Any],
        relations_config: Dict[str, Dict[str, Any]],
        user=None
    ) -> List[Any]:
        """
        Generate data with per_source relation strategy.
        
        This method generates N target objects for each source object, ensuring
        guaranteed coverage. For example, if 10 users exist and count_per_source=2,
        it will create 20 companies (2 per user).
        
        Args:
            model_key: Key from GENERATOR_CONFIG (e.g., 'company')
            config: Generator configuration dictionary
            relations_config: Relations configuration dictionary
            user: User instance for relations (optional)
        
        Returns:
            List of created model instances
        
        Process:
            1. Finds the first 'per_source' relation in relations_config
            2. Gets all source objects from the source model
            3. For each source object, generates N target objects (count_per_source)
            4. Creates relations between source and target objects
            5. Handles tags and other post-creation hooks
        
        Example:
            Config:
            ```python
            'company': {
                'model': 'company.Company',
                'relations': {
                    'user': {
                        'type': 'per_source',
                        'model': 'user.User',
                        'count_per_source': 2,  # 2 companies per user
                        'required': True,
                    },
                },
            }
            ```
            
            If 10 users exist:
            - Creates 20 companies (10 users × 2 companies)
            - Each user gets exactly 2 companies
        """
        import logging
        logger = logging.getLogger(__name__)
        
        logger.info(f"[GENERATOR] _generate_data_per_source START: model_key={model_key}")
        
        model_path = config['model']
        model_class = GeneratorService.get_model_class(model_path)
        
        logger.info(f"[GENERATOR] Model: {model_path}, Class: {model_class.__name__}")
        
        # Find the first per_source relation
        per_source_relation = None
        per_source_field = None
        for field_name, rel_config in relations_config.items():
            if rel_config.get('type') == 'per_source':
                per_source_relation = rel_config
                per_source_field = field_name
                break
        
        if not per_source_relation:
            logger.warning(f"[GENERATOR] No per_source relation found, falling back to standard generation")
            return GeneratorService.generate_data(model_key, user=user)
        
        # Get source model path from relation config
        source_model_path_from_config = per_source_relation.get('model')
        count_per_source = per_source_relation.get('count_per_source', 1)
        
        logger.info(f"[GENERATOR] Per-source config: source={source_model_path_from_config}, count_per_source={count_per_source}")
        
        # Find relation key
        relation_key = GeneratorService._find_relation_key(
            model_key, source_model_path_from_config
        )
        
        if not relation_key:
            # Try reverse direction
            relation_key = GeneratorService._find_relation_key_reverse(
                model_key, source_model_path_from_config
            )
        
        if not relation_key:
            logger.warning(f"[GENERATOR] No relation key found, falling back to standard generation")
            return GeneratorService.generate_data(model_key, user=user)
        
        logger.info(f"[GENERATOR] Found relation_key: {relation_key}")
        
        # Get relation config to determine source/target
        from sopira_magic.apps.relation.config import get_relation_config
        rel_config = get_relation_config(relation_key)
        if not rel_config:
            logger.warning(f"[GENERATOR] No relation config found for {relation_key}, falling back")
            return GeneratorService.generate_data(model_key, user=user)
        
        source_model_path = rel_config.get('source')
        target_model_path = rel_config.get('target')
        
        logger.info(f"[GENERATOR] Relation config: source={source_model_path}, target={target_model_path}")
        
        # Determine which model is source and which is target
        # The source model is the one we get objects from
        # The target model is the one we're generating
        if model_path == target_model_path:
            # We're generating target objects, source objects come from source_model_path
            source_model_class = GeneratorService.get_model_class(source_model_path)
        elif model_path == source_model_path:
            logger.warning(f"[GENERATOR] Generating source objects with per_source doesn't make sense, falling back")
            return GeneratorService.generate_data(model_key, user=user)
        else:
            logger.warning(f"[GENERATOR] Model mismatch, falling back")
            return GeneratorService.generate_data(model_key, user=user)
        
        # Get all source objects
        source_objects = list(source_model_class.objects.all())
        source_count = len(source_objects)
        
        logger.info(f"[GENERATOR] Found {source_count} source objects of type {source_model_path}")
        
        if not source_objects:
            if per_source_relation.get('required', False):
                logger.info(f"[GENERATOR] No source objects found, but required=True, creating one...")
                # If required, create at least one source object first
                # Find generator config for source model
                for key, cfg in get_all_generator_configs().items():
                    if cfg.get('model') == source_model_path:
                        GeneratorService.generate_data(key, count=1, user=user)
                        source_objects = list(source_model_class.objects.all())
                        source_count = len(source_objects)
                        logger.info(f"[GENERATOR] Created source object, now have {source_count} source objects")
                        break
            
            if not source_objects:
                logger.warning(f"[GENERATOR] Still no source objects, falling back to standard generation")
                return GeneratorService.generate_data(model_key, user=user)
        
        # Calculate expected count
        expected_count = source_count * count_per_source
        logger.info(f"[GENERATOR] Expected to create {expected_count} target objects ({source_count} sources × {count_per_source} per source)")
        
        # Generate target objects for each source object
        created_objects = []
        existing_count = model_class.objects.count()
        global_index = existing_count
        
        logger.info(f"[GENERATOR] Starting generation. Existing target objects: {existing_count}")
        
        for idx, source_obj in enumerate(source_objects, 1):
            logger.debug(f"[GENERATOR] Processing source object {idx}/{source_count}: {source_obj}")
            
            # Generate N target objects for this source object
            for i in range(count_per_source):
                global_index += 1
                index = global_index
                context = {}
                
                # Generate field values
                field_values = {}
                fields_config = config.get('fields', {})
                
                for field_name, field_config in fields_config.items():
                    try:
                        field = model_class._meta.get_field(field_name)
                        value = generate_field_value(field, field_config, index, context)
                        field_values[field_name] = value
                        context[field_name] = value
                    except Exception as e:
                        logger.debug(f"[GENERATOR] Skipping field {field_name}: {str(e)}")
                        continue
                
                # Create target object
                try:
                    if model_path == 'user.User':
                        if 'password' not in field_values:
                            field_values['password'] = 'pbkdf2_sha256$600000$dummy$dummy='
                        obj = model_class(**field_values)
                        obj.set_password('password123')
                        obj.save()
                    else:
                        obj = model_class.objects.create(**field_values)
                    
                    created_objects.append(obj)
                    
                    # Handle tags
                    if 'tags' in config.get('fields', {}):
                        tags_config = config['fields']['tags']
                        if tags_config.get('type') == 'dataset':
                            tags = generate_tags(tags_config.get('count'))
                            try:
                                from sopira_magic.apps.tag.models import Tag, TaggedItem
                                from django.contrib.contenttypes.models import ContentType
                                for tag_name in tags:
                                    tag, _ = Tag.objects.get_or_create(name=tag_name)
                                    TaggedItem.objects.get_or_create(
                                        tag=tag,
                                        content_type=ContentType.objects.get_for_model(obj.__class__),
                                        object_id=obj.id
                                    )
                            except Exception:
                                pass
                    
                    # Create relation between source and target
                    # Determine source and target based on relation config
                    obj_model_path = f"{obj._meta.app_label}.{obj.__class__.__name__}"
                    
                    if obj_model_path == target_model_path:
                        source_obj_rel = source_obj
                        target_obj_rel = obj
                    elif obj_model_path == source_model_path:
                        source_obj_rel = obj
                        target_obj_rel = source_obj
                    else:
                        logger.warning(f"[GENERATOR] Model mismatch when creating relation: {obj_model_path}")
                        continue
                    
                    try:
                        RelationService.create_relation(source_obj_rel, target_obj_rel, relation_key)
                    except Exception as e:
                        logger.warning(f"[GENERATOR] Failed to create relation {relation_key}: {str(e)}")
                    
                    # Handle other relations (non-per_source)
                    for relation_field, relation_config in relations_config.items():
                        if relation_field != per_source_field:
                            GeneratorService._create_relation(
                                obj, relation_field, relation_config, model_key, user
                            )
                
                except Exception as e:
                    logger.error(f"[GENERATOR] Failed to create target object for source {idx}: {str(e)}")
                    continue
            
            if idx % 10 == 0 or idx == source_count:
                logger.info(f"[GENERATOR] Progress: {idx}/{source_count} sources processed, {len(created_objects)} objects created so far")
        
        final_count = model_class.objects.count()
        logger.info(f"[GENERATOR] _generate_data_per_source COMPLETE: model_key={model_key}, created={len(created_objects)}, expected={expected_count}, total_in_db={final_count}")
        
        return created_objects
    
    @staticmethod
    def _create_relation(obj, relation_field: str, relation_config: Dict[str, Any], model_key: str, user=None):
        """
        Create relation for a generated object.
        
        This method handles relation creation for standard generation mode.
        For 'per_source' relations, use `_generate_data_per_source()` instead.
        
        Args:
            obj: The generated object (source or target)
            relation_field: Field name for the relation (for reference)
            relation_config: Relation configuration dictionary with keys:
                - type: 'random' | 'user' | 'per_source'
                - model: Target model path (e.g., 'user.User')
                - required: Boolean, if True creates target if missing
                - count_per_source: Integer, for 'per_source' type (not used here)
            model_key: Generator config key (e.g., 'company')
            user: User instance for 'user' relation type
        
        Relation Types:
            - 'random': Assigns a random existing object from target model
            - 'user': Uses provided user or first user
            - 'per_source': Not handled here, use `_generate_data_per_source()` instead
        
        Note:
            This method is called during standard generation. For 'per_source' relations,
            the generation strategy is different and handled in `_generate_data_per_source()`.
        """
        relation_type = relation_config.get('type')
        
        # Skip per_source here - it's handled in _generate_data_per_source()
        if relation_type == 'per_source':
            return
        target_model_path = relation_config.get('model')
        
        # Find relation key to determine source/target direction
        relation_key = GeneratorService._find_relation_key(
            model_key, target_model_path
        )
        
        if not relation_key:
            # Try reverse direction (maybe obj is target, not source)
            relation_key = GeneratorService._find_relation_key_reverse(
                model_key, target_model_path
            )
        
        if not relation_key:
            return  # No relation config found
        
        # Get relation config to determine source/target
        from sopira_magic.apps.relation.config import get_relation_config
        rel_config = get_relation_config(relation_key)
        if not rel_config:
            return
        
        source_model_path = rel_config.get('source')
        target_model_path_rel = rel_config.get('target')
        
        # Determine which object is source and which is target
        obj_model_path = f"{obj._meta.app_label}.{obj.__class__.__name__}"
        
        if relation_type == 'random':
            # Get random existing object from target model
            target_model = GeneratorService.get_model_class(target_model_path)
            existing_objects = list(target_model.objects.all())
            
            if not existing_objects and relation_config.get('required', False):
                # If required and no objects exist, create one first
                # Find generator config for target model
                for key, cfg in get_all_generator_configs().items():
                    if cfg.get('model') == target_model_path:
                        GeneratorService.generate_data(key, count=1, user=user)
                        existing_objects = list(target_model.objects.all())
                        break
            
            if existing_objects:
                related_obj = random.choice(existing_objects)
                related_obj_model_path = f"{related_obj._meta.app_label}.{related_obj.__class__.__name__}"
                
                # Determine source and target based on relation config
                if obj_model_path == source_model_path:
                    source_obj = obj
                    target_obj = related_obj
                elif obj_model_path == target_model_path_rel:
                    source_obj = related_obj
                    target_obj = obj
                else:
                    return  # Model mismatch
                
                try:
                    RelationService.create_relation(source_obj, target_obj, relation_key)
                except Exception as e:
                    # Log error but don't fail
                    import traceback
                    print(f"Warning: Failed to create relation {relation_key}: {str(e)}")
        
        elif relation_type == 'user':
            # Use provided user or get first user
            if user:
                related_obj = user
            else:
                from sopira_magic.apps.m_user.models import User
                related_obj = User.objects.first()
            
            if related_obj:
                related_obj_model_path = f"{related_obj._meta.app_label}.{related_obj.__class__.__name__}"
                
                # Determine source and target based on relation config
                if obj_model_path == source_model_path:
                    source_obj = obj
                    target_obj = related_obj
                elif obj_model_path == target_model_path_rel:
                    source_obj = related_obj
                    target_obj = obj
                else:
                    return  # Model mismatch
                
                try:
                    RelationService.create_relation(source_obj, target_obj, relation_key)
                except Exception as e:
                    # Log error but don't fail
                    import traceback
                    print(f"Warning: Failed to create relation {relation_key}: {str(e)}")
    
    @staticmethod
    def _find_relation_key(source_model_key: str, target_model_path: str) -> Optional[str]:
        """Find relation key from relation config (source -> target)."""
        from sopira_magic.apps.relation.config import RELATION_CONFIG
        
        # Map model keys to model paths
        model_path_map = {
            'company': 'company.Company',
            'factory': 'factory.Factory',
            'productionline': 'productionline.ProductionLine',
            'user': 'user.User',
            'photo': 'photo.Photo',
        }
        
        source_model_path = model_path_map.get(source_model_key, '')
        
        for key, config in RELATION_CONFIG.items():
            if (config.get('source') == source_model_path and 
                config.get('target') == target_model_path):
                return key
        
        return None
    
    @staticmethod
    def _find_relation_key_reverse(source_model_key: str, target_model_path: str) -> Optional[str]:
        """Find relation key from relation config (target -> source, reverse direction)."""
        from sopira_magic.apps.relation.config import RELATION_CONFIG
        
        # Map model keys to model paths
        model_path_map = {
            'company': 'company.Company',
            'factory': 'factory.Factory',
            'productionline': 'productionline.ProductionLine',
            'user': 'user.User',
            'photo': 'photo.Photo',
        }
        
        source_model_path = model_path_map.get(source_model_key, '')
        
        for key, config in RELATION_CONFIG.items():
            if (config.get('target') == source_model_path and 
                config.get('source') == target_model_path):
                return key
        
        return None
    
    @staticmethod
    def generate_seed_data(user=None, job_id: str = None, status_fn=None) -> Dict[str, int]:
        """
        Generate seed data for all configured models.
        Respects dependencies via 'depends_on' config - generates in correct order.
        
        Returns:
            Dictionary with counts of created objects per model
        """
        import logging
        logger = logging.getLogger(__name__)
        
        logger.info(f"[GENERATOR] generate_seed_data START")
        configs = get_all_generator_configs()
        
        # Build dependency graph from 'depends_on' in config
        dependencies = {}
        for key, config in configs.items():
            deps = config.get('depends_on', [])
            dependencies[key] = deps
        
        logger.info(f"[GENERATOR] Dependency graph: {dependencies}")

        # Progress tracker (across all records)
        total_target = sum(cfg.get('count', 0) for cfg in configs.values())
        progress = ProgressTracker(
            name="generate_seed_data",
            total=total_target,
            logger=logger,
            status_fn=status_fn,
            job_id=job_id,
        )
        progress.start()
        
        # Topological sort to generate in correct order
        generated = {}
        visited = set()
        
        def generate_recursive(key):
            if key in visited:
                return
            visited.add(key)
            
            # Generate dependencies first
            for dep in dependencies.get(key, []):
                generate_recursive(dep)
            
            # Generate this model
            if key not in generated:
                if job_id and is_cancel_requested(job_id):
                    logger.info(f"[GENERATOR] Cancel requested, stopping seed at model {key}")
                    return generated
                logger.info(f"[GENERATOR] Generating model: {key}")
                objects = GeneratorService.generate_data(key, user=user, progress=progress, job_id=job_id)
                generated[key] = len(objects)
                logger.info(f"[GENERATOR] Generated {key}: {len(objects)} objects")
                progress.step(len(objects), note=f"model {key}")
        
        # Generate all models
        for key in configs.keys():
            generate_recursive(key)
        
        logger.info(f"[GENERATOR] generate_seed_data COMPLETE: {generated}")
        progress.finish()
        return generated
    
    @staticmethod
    def clear_data(model_key: str, keep_count: int = 0):
        """
        Clear generated data for a model.
        
        Args:
            model_key: Key from GENERATOR_CONFIG
            keep_count: Number of records to keep (oldest)
        """
        import logging
        logger = logging.getLogger(__name__)
        
        config = get_generator_config(model_key)
        if not config:
            raise ValueError(f"Generator config '{model_key}' not found")
        
        model_path = config['model']
        model_class = GeneratorService.get_model_class(model_path)
        
        if keep_count > 0:
            # Keep oldest records
            to_delete = model_class.objects.order_by('created')[keep_count:]
            count = to_delete.count()
            try:
                to_delete.delete()
                logger.info(f"[GENERATOR] Cleared {model_key}: {count} records (kept {keep_count} oldest)")
                return count
            except Exception as e:
                error_msg = str(e)
                # If error is about STATE database (for User model), signal should handle it
                # But Django CASCADE might still try to delete from PRIMARY
                if 'state_tablestate' in error_msg or 'state_savedworkspace' in error_msg or 'state_environmentstate' in error_msg:
                    logger.warning(f"[GENERATOR] CASCADE deletion error for {model_key} (STATE database related): {error_msg}")
                    # Try to delete without CASCADE by using raw SQL or individual deletion
                    # For now, just log and re-raise - signal should handle STATE records
                    raise
                raise
        else:
            # Delete all
            count = model_class.objects.count()
            try:
                # Universal cross-database cascade delete is handled by core.signals
                # No hardcoded model-specific logic needed
                model_class.objects.all().delete()
                logger.info(f"[GENERATOR] Cleared {model_key}: {count} records")
                return count
            except Exception as e:
                error_msg = str(e)
                # If error is about cross-database CASCADE, core.signals should handle it
                # But Django CASCADE might still try to delete from wrong database
                if 'does not exist' in error_msg.lower() and ('state_' in error_msg.lower() or 'logging_' in error_msg.lower()):
                    logger.warning(f"[GENERATOR] Cross-database CASCADE error for {model_key}: {error_msg}")
                    logger.info(f"[GENERATOR] This should be handled by core.signals - re-raising for command to handle")
                    raise
                logger.error(f"[GENERATOR] Failed to clear {model_key}: {error_msg}")
                raise

# =============================================================================
# TAG SERVICES - Advanced tag assignment and removal
# =============================================================================

    @staticmethod
    @transaction.atomic
    def assign_tags_to_objects(user, model_key: str, count_per_object: int, object_ids: list = None) -> dict:
        """
        Assign tags to existing objects with optional ID filtering.
        
        Args:
            user: User instance for scope isolation
            model_key: Generator config key (e.g., 'factory', 'location')
            count_per_object: Number of tags to assign to each object
            object_ids: Optional list of specific object IDs to target
            
        Returns:
            Dictionary with assignment summary
        """
        import logging
        logger = logging.getLogger(__name__)
        
        logger.info(f"[TAG GENERATOR] assign_tags_to_objects START: model_key={model_key}, count={count_per_object}, object_ids={object_ids}")
        
        # Get generator config
        config = get_generator_config(model_key)
        if not config:
            raise ValueError(f"Generator config '{model_key}' not found")
        
        model_path = config['model']
        model_class = GeneratorService.get_model_class(model_path)
        
        # Get objects to tag (all or filtered by IDs)
        if object_ids:
            objects = model_class.objects.filter(id__in=object_ids)
        else:
            objects = model_class.objects.all()
        
        total_objects = objects.count()
        logger.info(f"[TAG GENERATOR] Found {total_objects} objects to tag")
        
        if total_objects == 0:
            return {
                "model_key": model_key,
                "total_objects": 0,
                "tags_assigned": 0,
                "message": "No objects found to tag"
            }
        
        # Get tag configuration
        tag_config = config.get('tag_assignments', {})
        tag_pool = tag_config.get('tag_pool')
        
        # Use global TAG_POOL if no specific pool defined
        if tag_pool is None:
            from .datasets import TAG_POOL
            tag_pool = TAG_POOL
        
        tags_assigned = 0
        
        for obj in objects:
            # Generate random tags for this object
            tags_to_assign = random.sample(tag_pool, min(count_per_object, len(tag_pool)))
            
            for tag_name in tags_to_assign:
                try:
                    # Get or create tag
                    tag, created = Tag.objects.get_or_create(
                        name=tag_name,
                        defaults={'color': '#3366FF', 'description': ''}
                    )
                    
                    # Create tagged item
                    TaggedItem.objects.get_or_create(
                        tag=tag,
                        content_type=ContentType.objects.get_for_model(obj),
                        object_id=obj.id
                    )
                    
                    tags_assigned += 1
                    
                except Exception as e:
                    logger.error(f"[TAG GENERATOR] Failed to assign tag '{tag_name}' to object {obj.id}: {str(e)}")
                    continue
        
        logger.info(f"[TAG GENERATOR] assign_tags_to_objects COMPLETE: assigned {tags_assigned} tags to {total_objects} objects")
        
        return {
            "model_key": model_key,
            "total_objects": total_objects,
            "tags_assigned": tags_assigned,
            "message": f"Assigned {tags_assigned} tags to {total_objects} objects"
        }

    @staticmethod
    @transaction.atomic
    def remove_tags_from_objects(user, model_key: str, count_per_object: int = None, object_ids: list = None) -> dict:
        """
        Remove tags from objects with flexible options.
        
        Args:
            user: User instance for scope isolation
            model_key: Generator config key
            count_per_object: Number of tags to remove per object (None = remove all)
            object_ids: Optional list of specific object IDs to target
            
        Returns:
            Dictionary with removal summary
        """
        import logging
        logger = logging.getLogger(__name__)
        
        logger.info(f"[TAG GENERATOR] remove_tags_from_objects START: model_key={model_key}, count={count_per_object}, object_ids={object_ids}")
        
        # Get generator config
        config = get_generator_config(model_key)
        if not config:
            raise ValueError(f"Generator config '{model_key}' not found")
        
        model_path = config['model']
        model_class = GeneratorService.get_model_class(model_path)
        
        # Get objects to process (all or filtered by IDs)
        if object_ids:
            objects = model_class.objects.filter(id__in=object_ids)
        else:
            objects = model_class.objects.all()
        
        total_objects = objects.count()
        logger.info(f"[TAG GENERATOR] Found {total_objects} objects to process")
        
        if total_objects == 0:
            return {
                "model_key": model_key,
                "total_objects": 0,
                "tags_removed": 0,
                "message": "No objects found to process"
            }
        
        tags_removed = 0
        
        for obj in objects:
            # Get all tags for this object
            content_type = ContentType.objects.get_for_model(obj)
            tags = TaggedItem.objects.filter(
                content_type=content_type,
                object_id=obj.id
            )
            
            if count_per_object is None:
                # Remove ALL tags
                count = tags.count()
                tags.delete()
                tags_removed += count
            else:
                # Remove N tags (or all if N > available)
                tags_to_remove = tags.order_by('created')[:count_per_object]
                count = tags_to_remove.count()
                tags_to_remove.delete()
                tags_removed += count
        
        logger.info(f"[TAG GENERATOR] remove_tags_from_objects COMPLETE: removed {tags_removed} tags from {total_objects} objects")
        
        return {
            "model_key": model_key,
            "total_objects": total_objects,
            "tags_removed": tags_removed,
            "message": f"Removed {tags_removed} tags from {total_objects} objects"
        }
