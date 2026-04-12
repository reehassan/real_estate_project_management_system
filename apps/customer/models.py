from django.db import models
from django.conf import settings
from django.core.validators import RegexValidator


# ── Validators ────────────────────────────────────────────────────
cnic_validator = RegexValidator(
    regex   = r'^\d{5}-\d{7}-\d{1}$',
    message = 'CNIC must be in format: 35202-1234567-1'
)

phone_validator = RegexValidator(
    regex   = r'^(\+92|0)[0-9]{10}$',
    message = 'Phone must be Pakistani format: 03001234567 or +923001234567'
)


# ─────────────────────────────────────────────────────────────────
class Customer(models.Model):
    """
    Extended profile for users with role=CUSTOMER.
    Linked to User via OneToOneField.

    Document structure mirrors DHA/Bahria-style PMS:
    - Profile photo (passport size)
    - CNIC front image
    - CNIC back image
    - Agreement copy (PDF or image)
    """

    # ── User Link ─────────────────────────────────────────────────
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete    = models.CASCADE,
        related_name = 'customer_profile'
    )

    # ── Personal Info ─────────────────────────────────────────────
    full_name = models.CharField(
        max_length = 200,
        null       = True,
        blank      = True
    )

    cnic = models.CharField(
        max_length = 15,
        unique     = True,
        db_index   = True,
        validators = [cnic_validator],
        help_text  = 'Format: 35202-1234567-1'
    )

    phone = models.CharField(
        max_length = 15,
        validators = [phone_validator],
        help_text  = 'Format: 03001234567'
    )

    phone_alt = models.CharField(
        max_length = 20,
        blank      = True,
        null       = True,
        validators = [phone_validator],
        help_text  = 'Optional alternate number'
    )

    guardian_name = models.CharField(
        max_length = 200,
        blank      = True,
        null       = True,
        help_text  = 'Father / Husband name — used in legal documents'
    )

    # ── Address ───────────────────────────────────────────────────
    address = models.TextField()
    city    = models.CharField(max_length=100)

    # ── Documents — Separated Like DHA/Bahria Standard ───────────
    profile_photo = models.ImageField(
        upload_to = 'customers/photos/',
        null      = True,
        blank     = True,
        help_text = 'Passport size photo'
    )

    cnic_front = models.ImageField(
        upload_to = 'customers/cnic/',
        null      = True,
        blank     = True,
        help_text = 'Front side of CNIC'
    )

    cnic_back = models.ImageField(
        upload_to = 'customers/cnic/',
        null      = True,
        blank     = True,
        help_text = 'Back side of CNIC'
    )

    agreement_copy = models.FileField(
        upload_to = 'customers/agreements/',
        null      = True,
        blank     = True,
        help_text = 'Signed agreement — PDF or image'
    )

    # ── Soft Delete ───────────────────────────────────────────────
    is_deleted = models.BooleanField(default=False)

    # ── Audit ─────────────────────────────────────────────────────
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null         = True,
        blank        = True,
        on_delete    = models.SET_NULL,
        related_name = 'customers_created'
    )

    updated_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null         = True,
        blank        = True,
        on_delete    = models.SET_NULL,
        related_name = 'customers_updated'
    )

    class Meta:
        ordering     = ['user__username']
        verbose_name = 'Customer'
        verbose_name_plural = 'Customers'

    def __str__(self):
        return f"{self.get_full_name()} — {self.cnic}"

    def get_full_name(self):
        name = self.full_name or self.user.get_full_name() or self.user.username
        return name

    @property
    def email(self):
        return self.user.email