#..............................................................
#   ~/sopira.magic/version_01/sopira_magic/apps/core/middleware.py
#   Core Middleware - Base middleware class
#   Foundation middleware for core functionality
#..............................................................

"""
Core Middleware - Base Middleware Class.

   Base middleware class for core functionality.
   Provides foundation for custom middleware implementations.

   Middleware:

   CoreMiddleware
   - Base middleware class following Django middleware pattern
   - Can be extended for custom request/response processing
   - Implements standard __init__ and __call__ methods

   Usage:
   ```python
   class CustomMiddleware(CoreMiddleware):
       def __call__(self, request):
           # Custom processing
           response = super().__call__(request)
           # Custom processing
           return response
   ```
"""


class CoreMiddleware:
    """Base middleware for core functionality."""
    
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        return response

