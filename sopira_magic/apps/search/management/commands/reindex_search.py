from django.core.management.base import BaseCommand

from sopira_magic.apps.search.services import SearchService


class Command(BaseCommand):
    help = "Full reindex Elasticsearch indexov z VIEWS_MATRIX (dynamic_search=True)."

    def add_arguments(self, parser):
        parser.add_argument(
            "--view",
            dest="view",
            default=None,
            help="Názov view z VIEWS_MATRIX (ak nie je zadané, reindexujú sa všetky).",
        )

    def handle(self, *args, **options):
        service = SearchService()
        if not service.enabled:
            self.stdout.write(self.style.WARNING("Elasticsearch je vypnutý (SEARCH_ELASTIC_ENABLED=0 alebo chýba ELASTICSEARCH_URL)."))
            self.stdout.write(self.style.WARNING("Reindex sa neuskutočnil."))
            return

        target_view = options.get("view")
        views = [target_view] if target_view else list(service.get_enabled_views().keys())

        for view_name in views:
            self.stdout.write(f"Reindexujem {view_name}...")
            ok, failed = service.recreate_index(view_name)
            self.stdout.write(self.style.SUCCESS(f"✓ {view_name}: {ok} indexed, {failed} failed"))

