from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    initial = True

    dependencies = [
        ("factory", "0001_initial"),
    ]

    operations = [
        migrations.CreateModel(
            name="CacheConfig",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("created", models.DateTimeField(auto_now_add=True)),
                ("updated", models.DateTimeField(auto_now=True)),
                ("key", models.CharField(db_index=True, max_length=255, unique=True)),
                ("config", models.JSONField(blank=True, default=dict)),
                ("ttl", models.IntegerField(default=3600)),
                ("enabled", models.BooleanField(default=True)),
            ],
            options={
                "verbose_name": "Cache Config",
                "verbose_name_plural": "Cache Configs",
            },
        ),
        migrations.CreateModel(
            name="FKOptionsCache",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("created", models.DateTimeField(auto_now_add=True)),
                ("updated", models.DateTimeField(auto_now=True)),
                ("field_name", models.CharField(db_index=True, max_length=100)),
                ("options", models.JSONField(blank=True, default=list)),
                ("record_count", models.IntegerField(default=0)),
                ("factories_count", models.IntegerField(default=0)),
                (
                    "factory",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="fk_options_cache",
                        to="factory.factory",
                    ),
                ),
            ],
            options={
                "verbose_name": "FK Options Cache",
                "verbose_name_plural": "FK Options Caches",
                "unique_together": {("field_name", "factory")},
            },
        ),
        migrations.AddIndex(
            model_name="fkoptionscache",
            index=models.Index(fields=["field_name"], name="fk_options__field_n_c06f5b_idx"),
        ),
        migrations.AddIndex(
            model_name="fkoptionscache",
            index=models.Index(fields=["field_name", "factory"], name="fk_options__field_n_2a6dd2_idx"),
        ),
    ]

