from rest_framework import serializers
from .models import Prescription


class PrescriptionSerializer(serializers.ModelSerializer):
    user_email = serializers.SerializerMethodField()
    image_url = serializers.SerializerMethodField()

    class Meta:
        model = Prescription
        fields = [
            'id', 'user', 'user_email', 'image', 'image_url',
            'notes', 'status', 'reviewed_by', 'reviewed_at',
            'review_notes', 'created_at', 'updated_at',
        ]
        read_only_fields = [
            'id', 'user', 'status', 'reviewed_by',
            'reviewed_at', 'review_notes', 'created_at', 'updated_at',
        ]

    def get_user_email(self, obj):
        return obj.user.email if obj.user else None

    def get_image_url(self, obj):
        request = self.context.get('request')
        if obj.image and request:
            return request.build_absolute_uri(obj.image.url)
        return obj.image.url if obj.image else None

    def to_representation(self, instance):
        data = super().to_representation(instance)
        if instance.user:
            data['user'] = {
                'id': instance.user.id,
                '_id': instance.user.id,
                'name': f"{instance.user.first_name} {instance.user.last_name}".strip() or instance.user.email,
                'email': instance.user.email,
            }
        else:
            data['user'] = None
        data['_id'] = instance.id
        data['file_path'] = instance.image.url if instance.image else ''
        data['file_name'] = instance.image.name.split('/')[-1] if instance.image else 'Prescription'
        return data
