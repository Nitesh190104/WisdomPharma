from rest_framework import serializers
from .models import Order, ORDER_STATUS_CHOICES, PAYMENT_STATUS_CHOICES


class OrderSerializer(serializers.ModelSerializer):
    user_email = serializers.SerializerMethodField()
    can_be_cancelled = serializers.SerializerMethodField()

    class Meta:
        model = Order
        fields = [
            'id', 'user', 'user_email', 'order_number',
            'items', 'subtotal', 'gst_total', 'discount', 'total',
            'status', 'payment_status', 'payment_method', 'type',
            'shipping_address', 'billing_address', 'notes',
            'prescription_id', 'estimated_delivery',
            'delivered_at', 'cancelled_at', 'cancellation_reason',
            'return_requested_at', 'return_reason',
            'return_reviewed_at', 'return_reviewed_by', 'return_reject_reason',
            'returned_at', 'can_be_cancelled',
            'created_at', 'updated_at',
        ]
        read_only_fields = [
            'id', 'user', 'order_number', 'created_at', 'updated_at',
            'delivered_at', 'cancelled_at', 'return_requested_at',
            'return_reviewed_at', 'returned_at',
        ]

    def get_user_email(self, obj):
        return obj.user.email if obj.user else None

    def get_can_be_cancelled(self, obj):
        return obj.can_be_cancelled()

    def to_representation(self, instance):
        data = super().to_representation(instance)
        if instance.user:
            data['user'] = {
                'id': instance.user.id,
                '_id': instance.user.id,
                'name': f"{instance.user.first_name} {instance.user.last_name}".strip() or instance.user.email,
                'email': instance.user.email,
                'phone': getattr(instance.user, 'phone', ''),
            }
        else:
            data['user'] = None
        data['_id'] = instance.id
        return data

    def create(self, validated_data):
        validated_data['order_number'] = Order.generate_order_number()
        return super().create(validated_data)
