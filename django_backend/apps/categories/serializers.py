from rest_framework import serializers
from .models import Category


class CategorySerializer(serializers.ModelSerializer):
    children = serializers.SerializerMethodField()
    parent_name = serializers.SerializerMethodField()

    class Meta:
        model = Category
        fields = [
            'id', 'name', 'slug', 'description', 'image', 'is_active',
            'parent', 'parent_name', 'children', 'created_at', 'updated_at',
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']

    def get_children(self, obj):
        # Only serialize one level of children to avoid deep recursion
        children = obj.children.filter(is_active=True)
        return CategorySerializer(children, many=True, context=self.context).data

    def get_parent_name(self, obj):
        return obj.parent.name if obj.parent else None
