from django.contrib import admin
from .models import Prescription

@admin.register(Prescription)
class PrescriptionAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'status', 'reviewed_by', 'reviewed_at', 'created_at')
    list_filter = ('status',)
    search_fields = ('user__email',)
    readonly_fields = ('created_at', 'updated_at')
