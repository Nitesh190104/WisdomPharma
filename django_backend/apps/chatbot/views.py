import re
import json
import logging
import google.generativeai as genai
from django.conf import settings
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from apps.authentication.permissions import IsAdminRole

logger = logging.getLogger(__name__)

CUSTOMER_SYSTEM_PROMPT = (
    "You are the warm, knowledgeable, and caring AI Virtual Pharmacist and Support Assistant for 'Wisdom Pharma'. "
    "Help customers with medicine information, device guidelines, and general health queries. "
    "Be concise, clear, and professional. Use markdown bold, lists, and headers."
)

ADMIN_SYSTEM_PROMPT = (
    "You are an admin assistant for Wisdom Pharma pharmacy management system. "
    "Help with inventory management, order processing, business analytics, and admin tasks."
)


class CustomerChatbotView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        message = request.data.get('message', '').strip()
        if not message:
            return Response({'success': False, 'message': 'Message is required'}, status=400)

        user = request.user if request.user and request.user.is_authenticated else None
        reply = None
        widget_data = {'type': 'text'}

        # Attempt Gemini call
        gemini_key = getattr(settings, 'GEMINI_API_KEY', None)
        if gemini_key:
            try:
                genai.configure(api_key=gemini_key)
                user_name = f"{user.first_name} {user.last_name}".strip() if user else 'Guest'
                role = getattr(user, 'role', 'consumer') if user else 'visitor'
                prompt = (
                    f"{CUSTOMER_SYSTEM_PROMPT}\n"
                    f"User Role: {role}\n"
                    f"User Name: {user_name}\n\n"
                    f"User: {message}"
                )
                model = genai.GenerativeModel('gemini-1.5-flash')
                res = model.generate_content(prompt)
                raw_text = res.text

                # Parse optional widget data if returned
                match = re.search(r'\[WIDGET_DATA\](.*?)\[/WIDGET_DATA\]', raw_text, re.DOTALL)
                if match:
                    raw_text = raw_text.replace(match.group(0), '').strip()
                    try:
                        widget_data = json.loads(match.group(1).strip())
                    except Exception:
                        pass
                reply = raw_text
            except Exception as e:
                logger.warning(f"Customer Gemini API error: {e}")

        # Fallback if Gemini is unavailable or failed
        if not reply:
            lower = message.lower()
            if 'headache' in lower or 'fever' in lower or 'pain' in lower:
                reply = (
                    "### 💊 Recommended Relief for Headache & Fever\n\n"
                    "For mild to moderate fever and headache, popular options in our pharmacy catalog include:\n"
                    "- **Dolo 650** (Paracetamol 650mg)\n"
                    "- **Crocin Advance** (Fast-acting paracetamol)\n"
                    "- **Paracetamol 500mg**\n\n"
                    "Drink plenty of water and take sufficient rest.\n\n"
                    "**⚠️ Disclaimer:** *I am an AI assistant. Please consult a qualified doctor or physician before starting any medication.*"
                )
                widget_data = {
                    'type': 'health_tips',
                    'tips': [{'title': 'Fever & Headache Care', 'description': 'Take paracetamol as directed, rest in a quiet space, and stay hydrated.', 'badge': 'Wellness'}]
                }
            elif 'order' in lower or 'track' in lower or 'status' in lower:
                if user and user.is_authenticated:
                    from apps.orders.models import Order
                    orders = Order.objects.filter(user=user).order_by('-created_at')[:3]
                    if orders.exists():
                        latest = orders.first()
                        reply = f"### 📦 Your Latest Order Status\n\nOrder **#{latest.order_number}** is currently **{latest.status.upper()}**.\nTotal Amount: ₹{latest.total}."
                        widget_data = {
                            'type': 'user_orders',
                            'orders': [{'id': o.id, 'order_number': o.order_number, 'total': float(o.total), 'status': o.status, 'date': o.created_at.strftime('%b %d, %Y')} for o in orders]
                        }
                    else:
                        reply = "You don't have any recent orders yet. Browse our medicines catalog to place your first order!"
                else:
                    reply = "To check your order details and track shipments, please **Sign In** to your account."
            else:
                reply = (
                    f"### 👋 Hello!\n\n"
                    f"I am your **Wisdom Pharmacy Care Assistant**. I can help you find medicines, answer general health product queries, and track orders.\n\n"
                    f"You can ask me about medications (e.g. *'Details for Dolo 650'*, *'Medicines for fever'*), medical supplies, or order tracking!\n\n"
                    f"**⚠️ Disclaimer:** *I am an AI assistant. Please consult a qualified doctor for clinical diagnosis.*"
                )

        return Response({
            'success': True,
            'message': reply,
            'data': widget_data,
        })


class AdminChatbotView(APIView):
    permission_classes = [IsAdminRole]

    def post(self, request):
        message = request.data.get('message', '').strip()
        if not message:
            return Response({'success': False, 'message': 'Message is required'}, status=400)

        reply = None
        gemini_key = getattr(settings, 'GEMINI_API_KEY', None)
        if gemini_key:
            try:
                genai.configure(api_key=gemini_key)
                model = genai.GenerativeModel('gemini-1.5-flash')
                res = model.generate_content(f"{ADMIN_SYSTEM_PROMPT}\n\nAdmin: {message}")
                reply = res.text
            except Exception as e:
                logger.warning(f"Admin Gemini API error: {e}")

        if not reply:
            reply = "I am the Wisdom Pharma Admin Assistant. You can monitor platform analytics, inventory stock levels, and review orders from your dashboard."

        return Response({
            'success': True,
            'message': reply,
            'data': {'response': reply},
        })
