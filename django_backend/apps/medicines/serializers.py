from rest_framework import serializers
from .models import Medicine
from apps.categories.serializers import CategorySerializer


class MedicineSerializer(serializers.ModelSerializer):
    category_name = serializers.SerializerMethodField()
    category_detail = CategorySerializer(source='category', read_only=True)
    retail_price_with_gst = serializers.SerializerMethodField()
    wholesale_price_with_gst = serializers.SerializerMethodField()
    is_low_stock = serializers.SerializerMethodField()
    is_expired = serializers.SerializerMethodField()

    class Meta:
        model = Medicine
        fields = [
            'id', 'medicine_name', 'description', 'category', 'category_name',
            'category_detail', 'stock', 'retail_price', 'wholesale_price',
            'gst_percentage', 'retail_price_with_gst', 'wholesale_price_with_gst',
            'expiry_date', 'manufacturer', 'prescription_required', 'image',
            'is_active', 'min_wholesale_qty', 'dosage', 'composition',
            'side_effects', 'usage_instructions', 'is_low_stock', 'is_expired',
            'created_at', 'updated_at', 'deleted_at',
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']

    def get_category_name(self, obj):
        return obj.category.name if obj.category else None

    def get_retail_price_with_gst(self, obj):
        return obj.retail_price_with_gst()

    def get_wholesale_price_with_gst(self, obj):
        return obj.wholesale_price_with_gst()

    def get_is_low_stock(self, obj):
        return obj.is_low_stock()

    def get_is_expired(self, obj):
        return obj.is_expired()
