from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):
    class Role(models.TextChoices): 
        OWNER = 'OWNER',    'Owner' # full access
        STAFF = 'STAFF',    'Staff' # operational access
        CUSTOMER = 'CUSTOMER',    'Customer' # portal access only

    Role = models.CharField(
        max_length=10,
        choices=Role.choices,
        default=Role.STAFF
    )
    class Meta:
        verbose_name = 'User'
        verbose_name_plural = 'Users'


