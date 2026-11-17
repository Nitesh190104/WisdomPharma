from django.core.mail import send_mail
from django.conf import settings
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny


class ContactView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        name = request.data.get('name', '')
        email = request.data.get('email', '')
        phone = request.data.get('phone', '')
        subject = request.data.get('subject', 'Contact Form Submission')
        message = request.data.get('message', '')

        if not (name and email and message):
            return Response({
                'success': False,
                'message': 'name, email and message are required',
            }, status=400)

        admin_email = getattr(settings, 'ADMIN_EMAIL', 'wisdompharma866@gmail.com')
        body = (
            f"Name: {name}\n"
            f"Email: {email}\n"
            f"Phone: {phone}\n\n"
            f"Message:\n{message}"
        )

        try:
            send_mail(
                subject=f"[Wisdom Pharma Contact] {subject}",
                message=body,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[admin_email],
                fail_silently=False,
            )
        except Exception as e:
            return Response({
                'success': False,
                'message': f'Failed to send email: {str(e)}',
            }, status=500)

        return Response({
            'success': True,
            'data': None,
            'message': 'Message sent successfully',
        })
