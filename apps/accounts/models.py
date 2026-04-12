from django.contrib.auth.models import AbstractUser
from django.db import models
from django.core.validators import EmailValidator


class User(AbstractUser):

    email = models.EmailField(
        unique=True,
        validators=[EmailValidator(message="Enter a valid email address")]
    )

    class Role(models.TextChoices):
        OWNER = 'OWNER', 'Owner'
        STAFF = 'STAFF', 'Staff'
        CUSTOMER = 'CUSTOMER', 'Customer'

    role = models.CharField(
        max_length=10,
        choices=Role.choices,
        default=Role.STAFF
    )

    def __str__(self):
        return self.username