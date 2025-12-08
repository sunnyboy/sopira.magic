#..............................................................
#   ~/sopira.magic/version_01/sopira_magic/apps/generator/field_generators.py
#   Field Generators - Auto-detecting field type generators
#   Adapts generated content based on Django field type
#..............................................................

"""
Field Generators - Auto-Detecting Field Type Generators.

   Generates values for Django model fields based on field type auto-detection.
   Automatically adapts generated content to match field constraints.

   Key Features:
   - Auto-detects Django field types (CharField, IntegerField, DateField, etc.)
   - Adapts generation based on field constraints (max_length, choices, etc.)
   - Supports configurable ranges (date_range, number_range, decimals, step)
   - Handles field dependencies (e.g., email from first_name + last_name)
    - Supports ForeignKey field generation via 'fk' type

   Field Type Support:
   - CharField, TextField: Random strings, templates, datasets
   - IntegerField, DecimalField: Random numbers with ranges and decimals
   - BooleanField: Random boolean values
   - DateField, DateTimeField, TimeField: Random dates/times with ranges
   - EmailField: Email generation from datasets
   - URLField: URL generation
   - UUIDField: UUID generation
    - ForeignKey: FK object selection via 'fk' type

   Generation Types:
   - template: Template-based (e.g., 'COMP-{index:03d}')
   - dataset: Predefined dataset lookup
   - copy: Copy from another field
   - lorem: Lorem Ipsum text
   - random: Random value based on field type
   - static: Static value
   - increment: Incremental value
    - choice: Random choice from list
    - fk: ForeignKey object selection (NEW)

FK Type Configuration:
    ```python
    'company': {
        'type': 'fk',
        'model': 'company.Company',
        'strategy': 'round_robin',  # or 'random', 'from_context'
        'nullable': True,           # optional, skip if no objects
        'filter': {'active': True}, # optional queryset filter
    }
    ```

   Usage:
   ```python
   from sopira_magic.apps.generator.field_generators import generate_field_value
    
    # Standard field
   field = User._meta.get_field('email')
   value = generate_field_value(field, {'type': 'dataset', 'dataset': 'email'}, 1, {})
    
    # FK field
    field = Factory._meta.get_field('company')
    value = generate_field_value(field, {'type': 'fk', 'model': 'company.Company'}, 1, {})
   ```
"""

import random
import string
from datetime import datetime, timedelta, date, time
from decimal import Decimal
from typing import Any, Dict
from django.db import models
from django.apps import apps

from .datasets import (
    generate_business_name,
    generate_full_name,
    generate_working_place,
    generate_material,
    generate_resource,
    generate_equipment,
    generate_country,
    generate_city,
    generate_street,
    generate_postal_code,
    generate_phone_number,
    generate_email,
    generate_address,
    generate_position,
    generate_user_role,
    generate_username,
    generate_photo_url,
    generate_tags,
)


class FieldGenerator:
    """Base class for field generators."""
    
    @staticmethod
    def generate(field_config: Dict[str, Any], index: int, context: Dict[str, Any] = None) -> Any:
        """Generate value for a field based on config."""
        context = context or {}
        field_type = field_config.get('type')
        
        if field_type == 'template':
            return FieldGenerator._generate_template(field_config, index, context)
        elif field_type == 'copy':
            return FieldGenerator._generate_copy(field_config, context)
        elif field_type == 'lorem':
            return FieldGenerator._generate_lorem(field_config)
        elif field_type == 'random':
            return FieldGenerator._generate_random(field_config)
        elif field_type == 'static':
            return field_config.get('value')
        elif field_type == 'increment':
            return FieldGenerator._generate_increment(field_config, index, context)
        elif field_type == 'dataset':
            return FieldGenerator._generate_from_dataset(field_config, index, context)
        elif field_type == 'fk':
            return FieldGenerator._generate_fk(field_config, index, context)
        elif field_type == 'choice':
            return FieldGenerator._generate_choice(field_config, index, context)
        else:
            return None
    
    @staticmethod
    def _generate_template(field_config: Dict[str, Any], index: int, context: Dict[str, Any]) -> str:
        """Generate value from template string."""
        template = field_config.get('template', '')
        try:
            return template.format(index=index, **context)
        except (KeyError, ValueError):
            return template.replace('{index}', str(index))
    
    @staticmethod
    def _generate_copy(field_config: Dict[str, Any], context: Dict[str, Any]) -> Any:
        """Copy value from another field."""
        from_field = field_config.get('from')
        return context.get(from_field)
    
    @staticmethod
    def _generate_lorem(field_config: Dict[str, Any]) -> str:
        """Generate Lorem Ipsum text."""
        words = field_config.get('words', 10)
        lorem_words = [
            'lorem', 'ipsum', 'dolor', 'sit', 'amet', 'consectetur', 'adipiscing',
            'elit', 'sed', 'do', 'eiusmod', 'tempor', 'incididunt', 'ut', 'labore',
            'et', 'dolore', 'magna', 'aliqua', 'enim', 'ad', 'minim', 'veniam',
            'quis', 'nostrud', 'exercitation', 'ullamco', 'laboris', 'nisi', 'ut',
            'aliquip', 'ex', 'ea', 'commodo', 'consequat', 'duis', 'aute', 'irure',
            'dolor', 'in', 'reprehenderit', 'voluptate', 'velit', 'esse', 'cillum',
            'dolore', 'eu', 'fugiat', 'nulla', 'pariatur', 'excepteur', 'sint',
            'occaecat', 'cupidatat', 'non', 'proident', 'sunt', 'in', 'culpa',
            'qui', 'officia', 'deserunt', 'mollit', 'anim', 'id', 'est', 'laborum'
        ]
        selected_words = random.choices(lorem_words, k=min(words, len(lorem_words)))
        return ' '.join(selected_words).capitalize() + '.'
    
    @staticmethod
    def _generate_random(field_config: Dict[str, Any]) -> Any:
        """Generate random value based on field type."""
        field_type = field_config.get('field_type', 'string')
        
        if field_type == 'string':
            length = field_config.get('length', 10)
            return ''.join(random.choices(string.ascii_letters + string.digits, k=length))
        elif field_type == 'integer':
            min_val = field_config.get('min', 0)
            max_val = field_config.get('max', 100)
            step = field_config.get('step', 1)
            # Generate value respecting step
            range_size = max_val - min_val
            steps = range_size // step
            return min_val + (random.randint(0, steps) * step)
        elif field_type == 'decimal':
            min_val = field_config.get('min', 0.0)
            max_val = field_config.get('max', 100.0)
            decimals = field_config.get('decimals', 2)
            step = field_config.get('step')
            if step:
                # Generate value respecting step
                steps = int((max_val - min_val) / step)
                value = min_val + (random.randint(0, steps) * step)
            else:
                value = random.uniform(min_val, max_val)
            return round(value, decimals)
        elif field_type == 'boolean':
            return random.choice([True, False])
        elif field_type == 'date':
            start_date = field_config.get('start_date')
            end_date = field_config.get('end_date')
            if isinstance(start_date, str):
                start_date = date.fromisoformat(start_date)
            if isinstance(end_date, str):
                end_date = date.fromisoformat(end_date)
            start_date = start_date or date(2020, 1, 1)
            end_date = end_date or date.today()
            days = (end_date - start_date).days
            return start_date + timedelta(days=random.randint(0, days))
        elif field_type == 'datetime':
            start = field_config.get('start')
            end = field_config.get('end')
            if isinstance(start, str):
                start = datetime.fromisoformat(start)
            if isinstance(end, str):
                end = datetime.fromisoformat(end)
            start = start or datetime(2020, 1, 1)
            end = end or datetime.now()
            delta = end - start
            return start + timedelta(seconds=random.randint(0, int(delta.total_seconds())))
        elif field_type == 'time':
            start_time = field_config.get('start_time')
            end_time = field_config.get('end_time')
            if isinstance(start_time, str):
                start_time = time.fromisoformat(start_time)
            if isinstance(end_time, str):
                end_time = time.fromisoformat(end_time)
            start_time = start_time or time(0, 0, 0)
            end_time = end_time or time(23, 59, 59)
            start_seconds = start_time.hour * 3600 + start_time.minute * 60 + start_time.second
            end_seconds = end_time.hour * 3600 + end_time.minute * 60 + end_time.second
            random_seconds = random.randint(start_seconds, end_seconds)
            hours = random_seconds // 3600
            minutes = (random_seconds % 3600) // 60
            seconds = random_seconds % 60
            return time(hours, minutes, seconds)
        else:
            return None
    
    @staticmethod
    def _generate_increment(field_config: Dict[str, Any], index: int, context: Dict[str, Any]) -> int:
        """Generate incremental value."""
        start = field_config.get('start', 1)
        step = field_config.get('step', 1)
        return start + (index * step)
    
    @staticmethod
    def _generate_fk(field_config: Dict[str, Any], index: int, context: Dict[str, Any] = None) -> Any:
        """
        Generate FK value by selecting from existing objects.
        
        Config options:
        - model: Model path (e.g., 'factory.Factory')
        - strategy: 'random' | 'round_robin' | 'from_context'
        - context_key: Key to get FK from context (for from_context strategy)
        - filter: Optional dict of filters to apply to queryset
        """
        context = context or {}
        model_path = field_config.get('model')
        strategy = field_config.get('strategy', 'random')
        
        if not model_path:
            return None
        
        # Get model class
        app_label, model_name = model_path.split('.')
        model_class = apps.get_model(app_label, model_name)
        
        # Get from context if specified
        if strategy == 'from_context':
            context_key = field_config.get('context_key')
            if context_key and context_key in context:
                return context[context_key]
        
        # Apply filters if specified
        queryset = model_class.objects.all()
        filters = field_config.get('filter', {})
        if filters:
            queryset = queryset.filter(**filters)
        
        # Select object based on strategy
        objects = list(queryset)
        if not objects:
            return None
        
        if strategy == 'round_robin':
            # Distribute evenly across objects
            return objects[index % len(objects)]
        else:  # random
            import random
            return random.choice(objects)
    
    @staticmethod
    def _generate_choice(field_config: Dict[str, Any], index: int, context: Dict[str, Any] = None) -> Any:
        """Generate value from list of choices."""
        import random
        choices = field_config.get('choices', [])
        if not choices:
            return None
        return random.choice(choices)
    
    @staticmethod
    def _generate_from_dataset(field_config: Dict[str, Any], index: int, context: Dict[str, Any] = None) -> Any:
        """Generate value from predefined dataset."""
        context = context or {}
        dataset = field_config.get('dataset')
        
        if dataset == 'business_name':
            return generate_business_name()
        elif dataset == 'first_name':
            first_name, _ = generate_full_name()
            return first_name
        elif dataset == 'last_name':
            _, last_name = generate_full_name()
            return last_name
        elif dataset == 'full_name':
            first_name, last_name = generate_full_name()
            return f"{first_name} {last_name}"
        elif dataset == 'working_place':
            return generate_working_place()
        elif dataset == 'material':
            return generate_material()
        elif dataset == 'resource':
            return generate_resource()
        elif dataset == 'equipment':
            return generate_equipment()
        elif dataset == 'country':
            return generate_country()
        elif dataset == 'city':
            return generate_city()
        elif dataset == 'street':
            return generate_street()
        elif dataset == 'postal_code' or dataset == 'zip' or dataset == 'psc':
            country = context.get('country') or field_config.get('country')
            return generate_postal_code(country)
        elif dataset == 'phone' or dataset == 'phone_number':
            country = context.get('country') or field_config.get('country')
            return generate_phone_number(country)
        elif dataset == 'email':
            first_name = context.get('first_name') or field_config.get('first_name')
            last_name = context.get('last_name') or field_config.get('last_name')
            domain = field_config.get('domain')
            return generate_email(first_name, last_name, domain)
        elif dataset == 'address' or dataset == 'full_address':
            country = context.get('country') or field_config.get('country')
            address_dict = generate_address(country)
            # Return full address string or dict based on config
            return address_dict if field_config.get('as_dict', False) else address_dict['full_address']
        elif dataset == 'position':
            return generate_position()
        elif dataset == 'user_role' or dataset == 'role':
            return generate_user_role()
        elif dataset == 'username':
            first_name = context.get('first_name') or field_config.get('first_name')
            last_name = context.get('last_name') or field_config.get('last_name')
            return generate_username(first_name, last_name, index)
        elif dataset == 'photo' or dataset == 'photo_url':
            name = context.get('full_name') or field_config.get('name')
            seed = context.get('username') or field_config.get('seed')
            return generate_photo_url(name, seed, thumbnail=False)
        elif dataset == 'thumbnail' or dataset == 'thumbnail_url':
            name = context.get('full_name') or field_config.get('name')
            seed = context.get('username') or field_config.get('seed')
            return generate_photo_url(name, seed, thumbnail=True)
        elif dataset == 'tags':
            count = field_config.get('count', None)
            tags = generate_tags(count)
            # Return as list or comma-separated string based on config
            return tags if field_config.get('as_list', False) else ', '.join(tags)
        else:
            return None


def generate_field_value(field: models.Field, field_config: Dict[str, Any], index: int, context: Dict[str, Any] = None) -> Any:
    """
    Generate value for a Django model field based on config.
    Auto-detects field type and adapts generated content accordingly.
    
    Args:
        field: Django model field instance
        field_config: Configuration for this field (supports date_range, time_range, number_range, decimals, step)
        index: Current index in generation loop
        context: Context dictionary with already generated values
    
    Returns:
        Generated value appropriate for the field type
    """
    context = context or {}
    
    # If config specifies a generator type, use it
    if 'type' in field_config:
        value = FieldGenerator.generate(field_config, index, context)
        if value is not None:
            return value
    
    # Auto-generate based on field type if no config
    # Extract range configs from field_config
    date_range = field_config.get('date_range', {})
    time_range = field_config.get('time_range', {})
    number_range = field_config.get('number_range', {})
    decimals = field_config.get('decimals')
    step = field_config.get('step')
    
    if isinstance(field, models.CharField):
        max_length = field.max_length or 255
        length = min(field_config.get('length', 20), max_length)
        return ''.join(random.choices(string.ascii_letters + string.digits, k=length))
    
    elif isinstance(field, models.TextField):
        words = field_config.get('words', 10)
        return FieldGenerator._generate_lorem({'words': words})
    
    elif isinstance(field, (models.IntegerField, models.BigIntegerField, models.SmallIntegerField, models.PositiveIntegerField)):
        # Check if this field should use aspect ratio (for width/height)
        aspect_ratio = field_config.get('aspect_ratio')
        if aspect_ratio and 'width' in context:
            # Calculate height based on width and aspect ratio
            # aspect_ratio = width/height, so height = width / aspect_ratio
            width = context.get('width')
            if width:
                height = int(width / aspect_ratio)
                # Round to nearest even number for better compression
                height = (height // 2) * 2
                return max(1, height)  # Ensure at least 1
        
        min_val = number_range.get('min', 0)
        max_val = number_range.get('max', 100)
        if step:
            range_size = max_val - min_val
            steps = range_size // step
            return min_val + (random.randint(0, steps) * step)
        return random.randint(min_val, max_val)
    
    elif isinstance(field, models.DecimalField):
        min_val = float(number_range.get('min', 0.0))
        max_val = float(number_range.get('max', 100.0))
        decimals_val = decimals if decimals is not None else field.decimal_places
        if step:
            steps = int((max_val - min_val) / step)
            value = min_val + (random.randint(0, steps) * step)
        else:
            value = random.uniform(min_val, max_val)
        return Decimal(str(round(value, decimals_val)))
    
    elif isinstance(field, models.FloatField):
        min_val = float(number_range.get('min', 0.0))
        max_val = float(number_range.get('max', 100.0))
        decimals_val = decimals if decimals is not None else 2
        if step:
            steps = int((max_val - min_val) / step)
            value = min_val + (random.randint(0, steps) * step)
        else:
            value = random.uniform(min_val, max_val)
        return round(value, decimals_val)
    
    elif isinstance(field, models.BooleanField):
        return field_config.get('value', random.choice([True, False]))
    
    elif isinstance(field, models.DateField):
        start_date = date_range.get('start')
        end_date = date_range.get('end')
        if isinstance(start_date, str):
            start_date = date.fromisoformat(start_date)
        if isinstance(end_date, str):
            end_date = date.fromisoformat(end_date)
        start_date = start_date or date(2020, 1, 1)
        end_date = end_date or date.today()
        days = (end_date - start_date).days
        return start_date + timedelta(days=random.randint(0, days))
    
    elif isinstance(field, models.DateTimeField):
        start = date_range.get('start')
        end = date_range.get('end')
        if isinstance(start, str):
            start = datetime.fromisoformat(start)
        if isinstance(end, str):
            end = datetime.fromisoformat(end)
        start = start or datetime(2020, 1, 1)
        end = end or datetime.now()
        delta = end - start
        return start + timedelta(seconds=random.randint(0, int(delta.total_seconds())))
    
    elif isinstance(field, models.TimeField):
        start_time = time_range.get('start')
        end_time = time_range.get('end')
        if isinstance(start_time, str):
            start_time = time.fromisoformat(start_time)
        if isinstance(end_time, str):
            end_time = time.fromisoformat(end_time)
        start_time = start_time or time(0, 0, 0)
        end_time = end_time or time(23, 59, 59)
        start_seconds = start_time.hour * 3600 + start_time.minute * 60 + start_time.second
        end_seconds = end_time.hour * 3600 + end_time.minute * 60 + end_time.second
        random_seconds = random.randint(start_seconds, end_seconds)
        hours = random_seconds // 3600
        minutes = (random_seconds % 3600) // 60
        seconds = random_seconds % 60
        return time(hours, minutes, seconds)
    
    elif isinstance(field, models.EmailField):
        # Use email dataset if available, otherwise generate simple email
        if 'dataset' in field_config and field_config.get('dataset') == 'email':
            first_name = context.get('first_name')
            last_name = context.get('last_name')
            return generate_email(first_name, last_name)
        return f"test{index}@example.com"
    
    elif isinstance(field, models.URLField):
        return f"https://example.com/item/{index}"
    
    elif isinstance(field, models.UUIDField):
        import uuid
        return uuid.uuid4()
    
    else:
        # Default: return None (field might have default)
        return None
