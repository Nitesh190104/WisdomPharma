from django.contrib import admin
from .models import Medicine

@admin.register(Medicine)
class MedicineAdmin(admin.ModelAdmin):
    list_display = (
        'medicine_name', 'category', 'retail_price', 'wholesale_price',
        'stock', 'prescription_required', 'is_active', 'expiry_date'
    )
    list_filter = ('is_active', 'prescription_required', 'category')
    search_fields = ('medicine_name', 'manufacturer', 'composition')
    readonly_fields = ('created_at', 'updated_at')
