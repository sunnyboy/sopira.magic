#..............................................................
#   ~/sopira.magic/version_01/sopira_magic/apps/m_measurement/models.py
#   Measurement Models - Core business entity
#..............................................................

"""
Measurement Models.

Measurement is a composite entity with multiple FK relationships.
Cannot use abstract base class due to complex FK structure.

Scoping: User → Company → Factory → Measurement
FK Chain: factory, location, carrier, driver, pot, [pit], [machine]
Children: Photo, Video (via MeasurementRelatedModel)
"""

from django.core.validators import MinValueValidator, MaxValueValidator, RegexValidator
from django.db import models
from django.utils.translation import gettext_lazy as _
from sopira_magic.apps.core.models import TimeStampedModel


class Measurement(TimeStampedModel):
    """
    Measurement - core business entity.
    
    Note: Explicit FKs (not via abstract base) due to:
    - Multiple FK relationships (7 entities)
    - Different null constraints per FK
    - Complex composite indexes
    """
    
    class PotSide(models.TextChoices):
        FRONT = "FRONT", _("FRONT")
        BACK = "BACK", _("BACK")
        NONE = "NONE", _("NONE")

    # ═══════════════════════════════════════════════════════════════
    # FK RELATIONSHIPS (scoping chain + lookups)
    # ═══════════════════════════════════════════════════════════════
    
    # Required FKs (nullable for migration compatibility)
    factory = models.ForeignKey(
        'factory.Factory',
        on_delete=models.PROTECT,
        related_name='measurements',
        null=True, blank=True,  # TODO: make NOT NULL after data migration
    )
    location = models.ForeignKey(
        'location.Location',
        on_delete=models.PROTECT,
        related_name='measurements',
        null=True, blank=True,
    )
    carrier = models.ForeignKey(
        'carrier.Carrier',
        on_delete=models.PROTECT,
        related_name='measurements',
        null=True, blank=True,
    )
    driver = models.ForeignKey(
        'driver.Driver',
        on_delete=models.PROTECT,
        related_name='measurements',
        null=True, blank=True,
    )
    pot = models.ForeignKey(
        'pot.Pot',
        on_delete=models.PROTECT,
        related_name='measurements',
        null=True, blank=True,
    )
    
    # Optional FKs
    pit = models.ForeignKey(
        'pit.Pit',
        on_delete=models.PROTECT,
        related_name='measurements',
        blank=True,
        null=True,
    )
    machine = models.ForeignKey(
        'machine.Machine',
        on_delete=models.PROTECT,
        related_name='measurements',
        blank=True,
        null=True,
    )

    # ═══════════════════════════════════════════════════════════════
    # MEASUREMENT DATA
    # ═══════════════════════════════════════════════════════════════

    # Dátum / čas dumpu
    dump_date = models.DateField(db_index=True)
    dump_time = models.TimeField(db_index=True)

    # Ostatné polia
    pit_number = models.CharField(
        max_length=50,
        blank=True,
        default="",
        help_text=_("Číslo jamy (text)")
    )
    
    pot_side = models.CharField(
        max_length=5,
        choices=PotSide.choices,
        default=PotSide.NONE,
        db_index=True
    )

    pot_knocks = models.PositiveIntegerField(
        validators=[MinValueValidator(0), MaxValueValidator(25)],
        help_text=_("Počet úderov (0..25). Validované aj voči Pot.knocks_max.")
    )
    
    # Nové pole - nameraný počet úderov
    pot_knocks_measurement = models.PositiveIntegerField(
        validators=[MinValueValidator(0), MaxValueValidator(25)],
        blank=True,
        null=True,
        help_text=_("Skutočne nameraný počet úderov pri meraní (0..25)")
    )

    pot_weight_kg = models.DecimalField(
        max_digits=9,
        decimal_places=3,
        validators=[MinValueValidator(0)],
        help_text=_("Weight of the pot (kg)")
    )

    # ROI teploty (°C)
    roi_temp_max_c = models.DecimalField(max_digits=7, decimal_places=3, null=True, blank=True)
    roi_temp_mean_c = models.DecimalField(max_digits=7, decimal_places=3, null=True, blank=True)
    roi_temp_min_c = models.DecimalField(max_digits=7, decimal_places=3, null=True, blank=True)

    # ROC hodnoty (°C)
    roc_value_min_c = models.DecimalField(max_digits=7, decimal_places=3, null=True, blank=True)
    roc_value_max_c = models.DecimalField(max_digits=7, decimal_places=3, null=True, blank=True)

    # Video a fotky (lokálne súbory, cloud URL-ky sú v separate modeloch)
    video_local_file = models.FileField(
        upload_to="videos/%Y/%m/",
        blank=True,
        null=True,
        help_text=_("Lokálna cesta/súbor pre video (uložené v MEDIA_ROOT)")
    )
    
    photo_local_file = models.FileField(
        upload_to="photos/%Y/%m/",
        blank=True,
        null=True,
        help_text=_("Lokálna cesta/súbor pre fotku (uložené v MEDIA_ROOT)")
    )

    # Grafy
    graph_roc = models.JSONField(
        blank=True,
        null=True,
        help_text=_("Pole bodov čas-hodnota pre ROC graf")
    )
    graph_temp = models.JSONField(
        blank=True,
        null=True,
        help_text=_("Pole bodov čas-hodnota pre TEMP graf")
    )

    # poznámky
    comment = models.TextField(blank=True, default="")
    note = models.TextField(blank=True, default="")

    _time_label_validator = RegexValidator(
        regex=r"^\d{2}:\d{2}:\d{2}(\.\d{1,3})?$",
        message=_("Očakávaný formát času je HH:MM:SS alebo HH:MM:SS.mmm"),
    )

    class Meta:
        verbose_name = _("Measurement")
        verbose_name_plural = _("Measurements")
        ordering = ["-dump_date", "-dump_time", "-id"]
        indexes = [
            models.Index(fields=["factory", "dump_date", "dump_time"]),
            models.Index(fields=["factory", "location"]),
            models.Index(fields=["dump_date", "dump_time"]),
            models.Index(fields=["pot_side"]),
        ]

    def __str__(self):
        return f"M#{self.pk} {self.dump_date} {self.dump_time}"

