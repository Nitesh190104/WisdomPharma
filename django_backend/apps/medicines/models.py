from django.db import models
from apps.categories.models import Category


class Medicine(models.Model):
    medicine_name = models.CharField(max_length=255)
    description = models.TextField(blank=True, default='')
    category = models.ForeignKey(
        Category, null=True, blank=True, on_delete=models.SET_NULL, related_name='medicines'
    )
    stock = models.IntegerField(default=0)
    retail_price = models.FloatField(default=0.0)
    wholesale_price = models.FloatField(default=0.0)
    gst_percentage = models.FloatField(default=0.0)
    expiry_date = models.DateField(null=True, blank=True)
    manufacturer = models.CharField(max_length=255, blank=True, default='')
    prescription_required = models.BooleanField(default=False)
    image = models.URLField(blank=True, default='')
    is_active = models.BooleanField(default=True)
    min_wholesale_qty = models.IntegerField(default=10)
    dosage = models.CharField(max_length=255, blank=True, default='')
    composition = models.TextField(blank=True, default='')
    side_effects = models.TextField(blank=True, default='')
    usage_instructions = models.TextField(blank=True, default='')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    deleted_at = models.DateTimeField(null=True, blank=True)  # soft delete

    class Meta:
        db_table = 'medicines'

    def __str__(self):
        return self.medicine_name

    def retail_price_with_gst(self):
        return self.retail_price + (self.retail_price * self.gst_percentage / 100)

    def wholesale_price_with_gst(self):
        return self.wholesale_price + (self.wholesale_price * self.gst_percentage / 100)

    def is_low_stock(self):
        return self.stock <= 10

    def is_expired(self):
        from django.utils import timezone
        return self.expiry_date and self.expiry_date < timezone.now().date()
