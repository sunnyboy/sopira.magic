from django.apps import AppConfig


class FkOptionsCacheConfig(AppConfig):
    name = "sopira_magic.apps.fk_options_cache"
    verbose_name = "FK Options Cache"

    def ready(self):
        # Import signal registrations
        from . import signals  # noqa: F401

