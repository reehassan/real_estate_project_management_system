from django.db import models
from django.utils.text import slugify


class Project(models.Model):

    class ProjectType(models.TextChoices):
        RESIDENTIAL  = 'RESIDENTIAL',  'Residential'
        COMMERCIAL   = 'COMMERCIAL',   'Commercial'
        INDUSTRIAL   = 'INDUSTRIAL',   'Industrial'
        AGRICULTURAL = 'AGRICULTURAL', 'Agricultural'
        OTHERS       = 'OTHERS',       'Others'

    class ProjectStatus(models.TextChoices):
        PLANNING  = 'PLANNING',  'Planning'
        ACTIVE    = 'ACTIVE',    'Active / Ongoing'
        ON_HOLD   = 'ON_HOLD',   'On Hold'
        COMPLETED = 'COMPLETED', 'Completed'
        CANCELLED = 'CANCELLED', 'Cancelled'

    PROPERTY_SUBTYPE_CHOICES = [
        # Residential
        ('HOUSE',            'House / Villa'),
        ('APARTMENT',        'Apartment / Flat'),
        ('RESIDENTIAL_PLOT', 'Residential Plot'),
        ('TOWNHOUSE',        'Townhouse'),
        ('VACATION_HOME',    'Vacation Home'),
        ('COOP_HOUSING',     'Cooperative Housing Society'),
        # Commercial
        ('OFFICE',           'Office Space'),
        ('SHOP',             'Shop / Retail Unit'),
        ('MALL',             'Shopping Mall'),
        ('MARKET',           'Sabzi Mandi / Market'),
        ('HOSPITALITY',      'Hotel / Motel / Resort'),
        ('RESTAURANT',       'Restaurant / Eatery'),
        ('RECREATION',       'Cinema / Theatre / Park'),
        ('PARKING',          'Parking Facility'),
        # Industrial
        ('FACTORY',          'Factory / Manufacturing Unit'),
        ('WAREHOUSE',        'Warehouse / Storage'),
        ('INDUSTRIAL_PARK',  'Industrial Park / Zone'),
        ('POWER_PLANT',      'Power Plant'),
        # Agricultural
        ('FARM',             'Cultivation Farm / Farmland'),
        ('ORCHARD',          'Orchard'),
        ('RANCH',            'Ranch / Livestock Farm'),
        ('FISH_FARM',        'Fish Farm'),
        ('RAW_LAND',         'Raw / Unserviced Plot'),
        ('SERVICED_PLOT',    'Serviced Plot'),
        # Mixed-Use
        ('MIXED_HIGHRISE',      'Mixed-Use High-Rise'),
        ('RETAIL_RESIDENTIAL',  'Retail / Residential'),
        # Special / Institutional
        ('SCHOOL',    'School / Educational Institution'),
        ('RELIGIOUS',  'Mosque / Religious Center'),
        ('HOSPITAL',   'Hospital / Healthcare Facility'),
        ('GOVT',       'Government / Administrative Building'),
        ('TOURISM',    'Tourism Infrastructure'),
    ]

    name         = models.CharField(max_length=200)
    slug         = models.SlugField(unique=True, blank=True)
    location     = models.TextField()
    city         = models.CharField(max_length=100)
    project_type = models.CharField(max_length=20, choices=ProjectType.choices)
    sub_type     = models.CharField(max_length=50, choices=PROPERTY_SUBTYPE_CHOICES, null=True, blank=True)
    status       = models.CharField(max_length=20, choices=ProjectStatus.choices, default=ProjectStatus.PLANNING)
    start_date   = models.DateField()
    total_area   = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    area_unit    = models.CharField(max_length=20, default='Kanal')
    description  = models.TextField(blank=True)
    logo         = models.ImageField(upload_to='projects/', null=True, blank=True)
    is_deleted   = models.BooleanField(default=False)
    created_at   = models.DateTimeField(auto_now_add=True)
    updated_at   = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-start_date']

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)