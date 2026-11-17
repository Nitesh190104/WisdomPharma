from django.db import models
from django.contrib.auth.models import AbstractUser


class User(AbstractUser):
    # Override username to not be required (use email as login)
    username = models.CharField(max_length=150, unique=False, blank=True, default='')
    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=20, blank=True, default='')
    role = models.CharField(
        max_length=20,
        choices=[('consumer', 'Consumer'), ('store', 'Store'), ('admin', 'Admin')],
        default='consumer'
    )
    address = models.TextField(blank=True, default='')
    city = models.CharField(max_length=100, blank=True, default='')
    state = models.CharField(max_length=100, blank=True, default='')
    pincode = models.CharField(max_length=10, blank=True, default='')
    avatar = models.URLField(blank=True, default='')
    is_active = models.BooleanField(default=True)
    is_approved = models.BooleanField(default=False)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']  # for createsuperuser

    class Meta:
        db_table = 'users'

    def is_admin_role(self):
        return self.role == 'admin'

    def is_store(self):
        return self.role == 'store'

    def is_consumer(self):
        return self.role == 'consumer'


class Business(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='business')
    business_name = models.CharField(max_length=255)
    gst_number = models.CharField(max_length=50, blank=True, default='')
    drug_license_number = models.CharField(max_length=100, blank=True, default='')
    is_verified = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'businesses'


class Otp(models.Model):
    email = models.EmailField(unique=True)
    otp = models.CharField(max_length=6)
    is_verified = models.BooleanField(default=False)
    expires_at = models.DateTimeField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'otps'
