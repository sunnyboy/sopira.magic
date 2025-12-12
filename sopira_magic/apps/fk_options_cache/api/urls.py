from django.urls import path

from . import views

urlpatterns = [
    path("fk-options-cache/", views.fk_options_cache_view, name="fk-options-cache"),
    path("fk-options-cache/rebuild/", views.fk_options_cache_rebuild_view, name="fk-options-cache-rebuild"),
    path("fk-options-cache/rebuild-scope/", views.fk_options_cache_rebuild_scope_view, name="fk-options-cache-rebuild-scope"),
]

