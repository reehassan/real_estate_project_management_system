from django.contrib.auth.models import AbstractUser
from django.db import models # base class used to create a Custom User Model

class User(AbstractUser):

    class Role(models.TextChoices):
        OWNER    = 'OWNER',    'Owner'
        STAFF    = 'STAFF',    'Staff'
        CUSTOMER = 'CUSTOMER', 'Customer'

    role = models.CharField(       
        max_length=10,
        choices=Role.choices,
        default=Role.STAFF
    )

    class Meta:
        verbose_name = 'User'
        verbose_name_plural = 'Users'


