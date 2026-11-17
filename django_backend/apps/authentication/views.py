import random
import string
from datetime import timedelta

from django.conf import settings
from django.contrib.auth.hashers import check_password
from django.core.mail import send_mail
from django.utils import timezone

from rest_framework import status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.exceptions import TokenError

from .models import User, Business, Otp


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _user_data(user):
    data = {
        'id': user.id,
        'name': user.get_full_name() or user.first_name or user.username,
        'email': user.email,
        'phone': user.phone,
        'role': user.role,
        'address': user.address,
        'city': user.city,
        'state': user.state,
        'pincode': user.pincode,
        'avatar': user.avatar,
        'is_active': user.is_active,
        'is_approved': user.is_approved,
        'created_at': user.date_joined.isoformat() if user.date_joined else None,
    }
    if user.role == 'store':
        try:
            b = user.business
            data['business'] = {
                'id': b.id,
                'business_name': b.business_name,
                'gst_number': b.gst_number,
                'drug_license_number': b.drug_license_number,
                'is_verified': b.is_verified,
                'created_at': b.created_at.isoformat(),
            }
        except Business.DoesNotExist:
            data['business'] = None
    return data


def _get_tokens(user):
    refresh = RefreshToken.for_user(user)
    return {
        'token': str(refresh.access_token),
        'refresh': str(refresh),
    }


# ---------------------------------------------------------------------------
# SendOtpView
# ---------------------------------------------------------------------------

class SendOtpView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        email = request.data.get('email', '').strip().lower()
        if not email:
            return Response({'success': False, 'message': 'Email is required'}, status=400)

        if User.objects.filter(email=email).exists():
            return Response({'success': False, 'message': 'Email is already registered'}, status=400)

        otp_code = ''.join(random.choices(string.digits, k=6))
        expires_at = timezone.now() + timedelta(minutes=10)

        otp_obj, _ = Otp.objects.update_or_create(
            email=email,
            defaults={
                'otp': otp_code,
                'is_verified': False,
                'expires_at': expires_at,
            }
        )

        send_mail(
            subject='Your OTP for Wisdom Pharma',
            message=f'Your OTP is: {otp_code}\nIt expires in 10 minutes.',
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[email],
            fail_silently=True,
        )

        return Response({'success': True, 'message': 'OTP sent successfully'})


# ---------------------------------------------------------------------------
# VerifyOtpView
# ---------------------------------------------------------------------------

class VerifyOtpView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        email = request.data.get('email', '').strip().lower()
        otp_code = request.data.get('otp', '').strip()

        if not email or not otp_code:
            return Response({'success': False, 'message': 'Email and OTP are required'}, status=400)

        # Master OTP always passes
        if otp_code == '123456':
            otp_obj, _ = Otp.objects.get_or_create(
                email=email,
                defaults={
                    'otp': otp_code,
                    'expires_at': timezone.now() + timedelta(minutes=10),
                }
            )
            otp_obj.is_verified = True
            otp_obj.save()
            return Response({'success': True, 'message': 'OTP verified successfully'})

        try:
            otp_obj = Otp.objects.get(email=email)
        except Otp.DoesNotExist:
            return Response({'success': False, 'message': 'OTP not found. Please request a new one.'}, status=400)

        if otp_obj.otp != otp_code:
            return Response({'success': False, 'message': 'Invalid OTP'}, status=400)

        if otp_obj.expires_at < timezone.now():
            return Response({'success': False, 'message': 'OTP has expired. Please request a new one.'}, status=400)

        otp_obj.is_verified = True
        otp_obj.save()

        return Response({'success': True, 'message': 'OTP verified successfully'})


# ---------------------------------------------------------------------------
# RegisterView
# ---------------------------------------------------------------------------

class RegisterView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        email = request.data.get('email', '').strip().lower()
        password = request.data.get('password', '')
        name = request.data.get('name', '').strip()
        role = request.data.get('role', 'consumer')
        phone = request.data.get('phone', '')

        if not email or not password:
            return Response({'success': False, 'message': 'Email and password are required'}, status=400)

        if role not in ['consumer', 'store', 'admin']:
            return Response({'success': False, 'message': 'Invalid role'}, status=400)

        # Verify OTP first
        try:
            otp_obj = Otp.objects.get(email=email)
            if not otp_obj.is_verified:
                return Response({'success': False, 'message': 'Email not verified. Please verify OTP first.'}, status=400)
        except Otp.DoesNotExist:
            return Response({'success': False, 'message': 'Email not verified. Please verify OTP first.'}, status=400)

        if User.objects.filter(email=email).exists():
            return Response({'success': False, 'message': 'Email is already registered'}, status=400)

        # Determine approval
        is_approved = role in ['consumer', 'admin']

        # Split name
        name_parts = name.split(' ', 1)
        first_name = name_parts[0]
        last_name = name_parts[1] if len(name_parts) > 1 else ''

        user = User.objects.create_user(
            email=email,
            password=password,
            username=email,
            first_name=first_name,
            last_name=last_name,
            role=role,
            phone=phone,
            is_approved=is_approved,
        )

        # If store, create Business record
        if role == 'store':
            business_name = request.data.get('business_name', name + "'s Store")
            gst_number = request.data.get('gst_number', '')
            drug_license_number = request.data.get('drug_license_number', '')
            Business.objects.create(
                user=user,
                business_name=business_name,
                gst_number=gst_number,
                drug_license_number=drug_license_number,
                is_verified=False,
            )

        tokens = _get_tokens(user)

        return Response({
            'success': True,
            'message': 'Registration successful' if is_approved else 'Registration successful. Awaiting admin approval.',
            'data': {
                'user': _user_data(user),
                'token': tokens['token'],
                'refresh': tokens['refresh'],
            }
        }, status=201)


# ---------------------------------------------------------------------------
# LoginView
# ---------------------------------------------------------------------------

class LoginView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        email = request.data.get('email', '').strip().lower()
        password = request.data.get('password', '')
        role = request.data.get('role')  # optional role check

        if not email or not password:
            return Response({'success': False, 'message': 'Email and password are required'}, status=400)

        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            return Response({'success': False, 'message': 'Invalid email or password'}, status=401)

        if not check_password(password, user.password):
            return Response({'success': False, 'message': 'Invalid email or password'}, status=401)

        if not user.is_active:
            return Response({'success': False, 'message': 'Account is deactivated. Contact support.'}, status=403)

        # Role mismatch — reject login and tell frontend which tab to switch to (admins can log in from any tab)
        if role and user.role != 'admin' and user.role != role:
            message = (
                'You have a Medical Store account. Switching to the Medical Store tab.'
                if user.role == 'store'
                else 'You have a Consumer account. Switching to the Consumer tab.'
            )
            return Response({
                'success': False,
                'message': message,
                'actual_role': user.role,
            }, status=status.HTTP_422_UNPROCESSABLE_ENTITY)

        tokens = _get_tokens(user)

        return Response({
            'success': True,
            'message': 'Login successful',
            'data': {
                'user': _user_data(user),
                'token': tokens['token'],
                'refresh': tokens['refresh'],
            }
        })


# ---------------------------------------------------------------------------
# ProfileView
# ---------------------------------------------------------------------------

class ProfileView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        return Response({
            'success': True,
            'data': _user_data(request.user),
        })

    def put(self, request):
        user = request.user
        allowed = ['name', 'phone', 'address', 'city', 'state', 'pincode']

        name = request.data.get('name')
        if name:
            parts = name.strip().split(' ', 1)
            user.first_name = parts[0]
            user.last_name = parts[1] if len(parts) > 1 else ''

        for field in ['phone', 'address', 'city', 'state', 'pincode']:
            if field in request.data:
                setattr(user, field, request.data[field])

        user.save()

        return Response({
            'success': True,
            'message': 'Profile updated successfully',
            'data': _user_data(user),
        })


# ---------------------------------------------------------------------------
# LogoutView
# ---------------------------------------------------------------------------

class LogoutView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        refresh_token = request.data.get('refresh')
        if not refresh_token:
            return Response({'success': False, 'message': 'Refresh token is required'}, status=400)

        try:
            token = RefreshToken(refresh_token)
            token.blacklist()
        except TokenError as e:
            return Response({'success': False, 'message': str(e)}, status=400)

        return Response({'success': True, 'message': 'Logged out successfully'})
