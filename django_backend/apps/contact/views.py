import threading
import logging
from django.core.mail import send_mail
from django.conf import settings
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny

logger = logging.getLogger(__name__)


def _send_contact_email_async(subject, message, recipient_list):
    def _task():
        try:
            send_mail(
                subject=subject,
                message=message,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=recipient_list,
                fail_silently=True,
            )
        except Exception as e:
            logger.warning("Contact email async send failed: %s", e)

    threading.Thread(target=_task, daemon=True).start()


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

        _send_contact_email_async(
            subject=f"[Wisdom Pharma Contact] {subject}",
            message=body,
            recipient_list=[admin_email],
        )

        return Response({
            'success': True,
            'data': None,
            'message': 'Message sent successfully',
        })
