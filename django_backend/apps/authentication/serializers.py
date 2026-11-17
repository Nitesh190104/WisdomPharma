from rest_framework import serializers
from django.contrib.auth import authenticate
from .models import User, Business, Otp


class BusinessSerializer(serializers.ModelSerializer):
    class Meta:
        model = Business
        fields = [
            'id', 'business_name', 'gst_number', 'drug_license_number',
            'is_verified', 'created_at', 'updated_at',
        ]
        read_only_fields = ['id', 'is_verified', 'created_at', 'updated_at']


class UserSerializer(serializers.ModelSerializer):
    business = BusinessSerializer(read_only=True)

    class Meta:
        model = User
        fields = [
            'id', 'username', 'email', 'first_name', 'last_name',
            'phone', 'role', 'address', 'city', 'state', 'pincode',
            'avatar', 'is_active', 'is_approved', 'business',
            'date_joined', 'last_login',
        ]
        read_only_fields = ['id', 'date_joined', 'last_login', 'is_approved']


class RegisterSerializer(serializers.Serializer):
    name = serializers.CharField(max_length=255)
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True, min_length=6)
    phone = serializers.CharField(max_length=20, required=False, default='')
    role = serializers.ChoiceField(
        choices=['consumer', 'store', 'admin'], default='consumer'
    )
    # Store-only fields
    business_name = serializers.CharField(max_length=255, required=False, default='')
    gst_number = serializers.CharField(max_length=50, required=False, default='')
    drug_license_number = serializers.CharField(max_length=100, required=False, default='')

    def validate_email(self, value):
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError("A user with this email already exists.")
        return value

    def validate(self, data):
        if data.get('role') == 'store' and not data.get('business_name'):
            raise serializers.ValidationError(
                {"business_name": "Business name is required for store accounts."}
            )
        return data

    def create(self, validated_data):
        name = validated_data.pop('name')
        business_name = validated_data.pop('business_name', '')
        gst_number = validated_data.pop('gst_number', '')
        drug_license_number = validated_data.pop('drug_license_number', '')
        password = validated_data.pop('password')

        # Split name into first/last
        parts = name.strip().split(' ', 1)
        first_name = parts[0]
        last_name = parts[1] if len(parts) > 1 else ''

        user = User.objects.create_user(
            email=validated_data['email'],
            password=password,
            first_name=first_name,
            last_name=last_name,
            phone=validated_data.get('phone', ''),
            role=validated_data.get('role', 'consumer'),
        )

        if user.role == 'store' and business_name:
            Business.objects.create(
                user=user,
                business_name=business_name,
                gst_number=gst_number,
                drug_license_number=drug_license_number,
            )

        return user


class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)
    role = serializers.ChoiceField(
        choices=['consumer', 'store', 'admin'], required=False, allow_null=True
    )

    def validate(self, data):
        email = data.get('email')
        password = data.get('password')
        role = data.get('role')

        user = authenticate(username=email, password=password)
        if not user:
            raise serializers.ValidationError("Invalid email or password.")
        if not user.is_active:
            raise serializers.ValidationError("This account has been deactivated.")
        if role and user.role != role:
            raise serializers.ValidationError(
                f"This account does not have the '{role}' role."
            )

        data['user'] = user
        return data


class ProfileUpdateSerializer(serializers.ModelSerializer):
    name = serializers.CharField(max_length=255, required=False)

    class Meta:
        model = User
        fields = ['name', 'phone', 'address', 'city', 'state', 'pincode', 'avatar']

    def validate_name(self, value):
        return value  # handled in update()

    def update(self, instance, validated_data):
        name = validated_data.pop('name', None)
        if name:
            parts = name.strip().split(' ', 1)
            instance.first_name = parts[0]
            instance.last_name = parts[1] if len(parts) > 1 else ''
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        return instance


class OtpSerializer(serializers.ModelSerializer):
    class Meta:
        model = Otp
        fields = ['id', 'email', 'is_verified', 'expires_at', 'created_at']
        read_only_fields = ['id', 'is_verified', 'created_at']
