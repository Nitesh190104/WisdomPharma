from django.db import models
from django.conf import settings

ORDER_STATUS_CHOICES = [
    ('pending', 'Pending'),
    ('confirmed', 'Confirmed'),
    ('processing', 'Processing'),
    ('shipped', 'Shipped'),
    ('delivered', 'Delivered'),
    ('cancelled', 'Cancelled'),
    ('return_requested', 'Return Requested'),
    ('returned', 'Returned'),
]

PAYMENT_STATUS_CHOICES = [
    ('pending', 'Pending'),
    ('paid', 'Paid'),
    ('refunded', 'Refunded'),
]


class Order(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='orders'
    )
    order_number = models.CharField(max_length=100, unique=True)
    # items stored as JSON array: [{medicine_id, medicine_name, quantity, price, gst}]
    items = models.JSONField(default=list)
    subtotal = models.FloatField(default=0.0)
    gst_total = models.FloatField(default=0.0)
    discount = models.FloatField(default=0.0)
    total = models.FloatField(default=0.0)
    status = models.CharField(max_length=30, choices=ORDER_STATUS_CHOICES, default='pending')
    payment_status = models.CharField(max_length=20, choices=PAYMENT_STATUS_CHOICES, default='pending')
    payment_method = models.CharField(max_length=50, default='cod')
    razorpay_payment_id = models.CharField(max_length=255, blank=True, null=True)
    type = models.CharField(
        max_length=20,
        choices=[('retail', 'Retail'), ('wholesale', 'Wholesale')],
        default='retail'
    )
    shipping_address = models.JSONField(default=dict)
    billing_address = models.JSONField(default=dict)
    notes = models.TextField(blank=True, default='')
    prescription_id = models.IntegerField(null=True, blank=True)
    estimated_delivery = models.DateField(null=True, blank=True)
    delivered_at = models.DateTimeField(null=True, blank=True)
    cancelled_at = models.DateTimeField(null=True, blank=True)
    cancellation_reason = models.TextField(blank=True, default='')
    return_requested_at = models.DateTimeField(null=True, blank=True)
    return_reason = models.TextField(blank=True, default='')
    return_reviewed_at = models.DateTimeField(null=True, blank=True)
    return_reviewed_by = models.IntegerField(null=True, blank=True)
    return_reject_reason = models.TextField(blank=True, default='')
    returned_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'orders'

    def __str__(self):
        return self.order_number

    @staticmethod
    def generate_order_number():
        import uuid
        import datetime
        return f"WP-{uuid.uuid4().hex[:8].upper()}-{datetime.date.today().strftime('%Y%m%d')}"

    def can_be_cancelled(self):
        return self.status in ['pending', 'confirmed']
