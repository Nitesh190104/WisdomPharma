from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User, Business, Otp

@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = ('email', 'first_name', 'last_name', 'role', 'phone', 'is_approved', 'is_active', 'is_staff')
    list_filter = ('role', 'is_approved', 'is_active', 'is_staff')
    search_fields = ('email', 'first_name', 'last_name', 'phone')
    ordering = ('email',)
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Personal Info', {'fields': ('first_name', 'last_name', 'phone', 'avatar', 'address', 'city', 'state', 'pincode')}),
        ('Permissions & Roles', {'fields': ('role', 'is_approved', 'is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('Important dates', {'fields': ('last_login', 'date_joined')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'first_name', 'last_name', 'password', 'role'),
        }),
    )

@admin.register(Business)
class BusinessAdmin(admin.ModelAdmin):
    list_display = ('business_name', 'user', 'gst_number', 'drug_license_number', 'is_verified', 'created_at')
    list_filter = ('is_verified',)
    search_fields = ('business_name', 'gst_number', 'drug_license_number', 'user__email')

@admin.register(Otp)
class OtpAdmin(admin.ModelAdmin):
    list_display = ('email', 'otp', 'is_verified', 'expires_at', 'created_at')
    search_fields = ('email',)
