#..............................................................
#   ~/sopira.magic/version_01/sopira_magic/apps/core/utils.py
#   Core Utils - Common utility functions
#   Shared helper functions for model introspection
#..............................................................

"""
Core Utils - Common Utility Functions.

   Shared utility functions for model introspection and common operations.
   Provides helper functions used across multiple apps.

   Functions:

   1. get_model_name(model_class)
      - Returns the name of a model class
      - Example: get_model_name(User) → "User"

   2. get_app_label(model_class)
      - Returns the app label of a model class
      - Example: get_app_label(User) → "user"

   Usage:
   ```python
   from sopira_magic.apps.core.utils import get_model_name, get_app_label
   model_name = get_model_name(User)
   app_label = get_app_label(User)
   ```
"""


def get_model_name(model_class):
    """Get model name from model class."""
    return model_class.__name__


def get_app_label(model_class):
    """Get app label from model class."""
    return model_class._meta.app_label

