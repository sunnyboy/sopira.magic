#!/bin/bash
# Helper script to create app structure

create_app() {
    APP_NAME=$1
    APP_DIR="sopira_magic/apps/$APP_NAME"
    
    mkdir -p "$APP_DIR/migrations"
    
    # __init__.py
    echo "# $APP_NAME application" > "$APP_DIR/__init__.py"
    
    # apps.py
    cat > "$APP_DIR/apps.py" << APPEOF
from django.apps import AppConfig


class ${APP_NAME^}Config(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'sopira_magic.apps.$APP_NAME'
    verbose_name = '${APP_NAME^}'
APPEOF
    
    # models.py
    echo "# $APP_NAME models" > "$APP_DIR/models.py"
    echo "" >> "$APP_DIR/models.py"
    echo "from django.db import models" >> "$APP_DIR/models.py"
    echo "from sopira_magic.apps.core.models import TimeStampedModel, NamedWithCodeModel" >> "$APP_DIR/models.py"
    
    # admin.py
    echo "from django.contrib import admin" > "$APP_DIR/admin.py"
    echo "" >> "$APP_DIR/admin.py"
    echo "# Register your models here." >> "$APP_DIR/admin.py"
    
    # migrations/__init__.py
    echo "# $APP_NAME migrations" > "$APP_DIR/migrations/__init__.py"
    
    echo "Created $APP_NAME"
}

# Create all apps
create_app "shared"
create_app "user"
create_app "authentification"
create_app "company"
create_app "factory"
create_app "productionline"
create_app "utility"
create_app "equipment"
create_app "resource"
create_app "worker"
create_app "material"
create_app "process"
create_app "endpoint"
create_app "dashboard"
create_app "search"
create_app "notification"
create_app "reporting"
create_app "analytics"
create_app "alarm"
create_app "audit"
create_app "logging"
create_app "file_storage"
create_app "document"
create_app "video"
create_app "photo"
create_app "tag"
create_app "scheduler"
create_app "caching"
create_app "state"
create_app "internationalization"
create_app "impex"
create_app "api"
create_app "mobileapp"
create_app "relation"
create_app "generator"

echo "All apps created!"
