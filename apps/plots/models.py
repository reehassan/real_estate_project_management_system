from django.db import models
from django.conf import settings
from apps.projects.models import Project


class Plot(models.Model):
    """
    Represents an individual plot within a real estate project.
    A project can have many plots. Plot numbers must be unique per project.
    """

    class PlotStatus(models.TextChoices):
        AVAILABLE = 'AVAILABLE', 'Available'
        BOOKED    = 'BOOKED',    'Booked'
        SOLD      = 'SOLD',      'Sold'
        RESERVED  = 'RESERVED',  'Reserved'

    class SizeUnit(models.TextChoices):
        MARLA = 'MARLA', 'Marla'
        KANAL = 'KANAL', 'Kanal'
        SQFT  = 'SQFT',  'Square Feet'
        SQYD  = 'SQYD',  'Square Yards'

    class PlotCategory(models.TextChoices):
        RESIDENTIAL  = 'RESIDENTIAL',  'Residential'
        COMMERCIAL   = 'COMMERCIAL',   'Commercial'
        INDUSTRIAL   = 'INDUSTRIAL',   'Industrial'
        AGRICULTURAL = 'AGRICULTURAL', 'Agricultural'

    # ── Core Fields ──────────────────────────────────────────────
    project     = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='plots')
    plot_number = models.CharField(max_length=50)
    category    = models.CharField(max_length=20, choices=PlotCategory.choices)
    status      = models.CharField(max_length=20, choices=PlotStatus.choices, default=PlotStatus.AVAILABLE)
    area        = models.DecimalField(max_digits=10, decimal_places=2)
    area_unit   = models.CharField(max_length=20, choices=SizeUnit.choices, default=SizeUnit.MARLA)
    price       = models.DecimalField(max_digits=14, decimal_places=2, null=True, blank=True)
    description = models.TextField(blank=True)
    is_corner   = models.BooleanField(default=False)
    is_deleted  = models.BooleanField(default=False)

    # ── Who & When ───────────────────────────────────────────────
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True, blank=True,
        on_delete=models.SET_NULL,
        related_name='plots_created'
    )
    updated_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True, blank=True,
        on_delete=models.SET_NULL,
        related_name='plots_updated'
    )

    class Meta:
        ordering        = ['project', 'plot_number']
        unique_together = [['project', 'plot_number']]

    def __str__(self):
        return f"{self.project.name} — Plot {self.plot_number}"


# ─────────────────────────────────────────────────────────────────
class PlotAuditLog(models.Model):
    """
    Permanent, append-only log of every change made to a Plot.
    Never edit or delete rows from this table.
    """

    class Action(models.TextChoices):
        CREATED  = 'CREATED',  'Created'
        UPDATED  = 'UPDATED',  'Updated'
        DELETED  = 'DELETED',  'Deleted'
        RESTORED = 'RESTORED', 'Restored'

    plot       = models.ForeignKey(Plot, on_delete=models.CASCADE, related_name='audit_logs')
    action     = models.CharField(max_length=20, choices=Action.choices)
    changed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        on_delete=models.SET_NULL,
        related_name='plot_audit_logs'
    )
    changed_at = models.DateTimeField(auto_now_add=True)
    field_name = models.CharField(max_length=100, blank=True)
    old_value  = models.TextField(blank=True, null=True)
    new_value  = models.TextField(blank=True, null=True)
    note       = models.TextField(blank=True)

    class Meta:
        ordering = ['-changed_at']

    def __str__(self):
        return f"{self.plot} | {self.action} | {self.changed_by} | {self.changed_at:%Y-%m-%d %H:%M}"