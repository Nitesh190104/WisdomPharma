from rest_framework import serializers
from .models import Cart, CartItem
from apps.medicines.serializers import MedicineSerializer


class CartItemSerializer(serializers.ModelSerializer):
    medicine = MedicineSerializer(read_only=True)
    medicine_id = serializers.IntegerField(write_only=True)
    subtotal = serializers.SerializerMethodField()

    class Meta:
        model = CartItem
        fields = ['id', 'medicine', 'medicine_id', 'quantity', 'subtotal']
        read_only_fields = ['id']

    def get_subtotal(self, obj):
        try:
            return obj.medicine.retail_price_with_gst() * obj.quantity
        except Exception:
            return 0.0


class CartSerializer(serializers.ModelSerializer):
    items = CartItemSerializer(many=True, read_only=True)
    total_items = serializers.SerializerMethodField()
    total_amount = serializers.SerializerMethodField()

    class Meta:
        model = Cart
        fields = ['id', 'user', 'items', 'total_items', 'total_amount', 'created_at', 'updated_at']
        read_only_fields = ['id', 'user', 'created_at', 'updated_at']

    def get_total_items(self, obj):
        return sum(item.quantity for item in obj.items.all())

    def get_total_amount(self, obj):
        total = 0.0
        for item in obj.items.all():
            try:
                total += item.medicine.retail_price_with_gst() * item.quantity
            except Exception:
                pass
        return round(total, 2)
