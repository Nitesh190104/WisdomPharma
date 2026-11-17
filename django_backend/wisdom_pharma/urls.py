import mimetypes
from pathlib import Path
from django.contrib import admin
from django.urls import path, re_path, include
from django.conf import settings
from django.conf.urls.static import static
from django.views.static import serve
from django.http import JsonResponse, HttpResponseRedirect

# Register .avif mimetype for modern browsers
mimetypes.add_type('image/avif', '.avif')

# Path to the Medicines images directory (handles standalone deploy or repo root)
MEDICINES_IMAGE_DIR = Path(settings.BASE_DIR) / 'Medicines'
if not MEDICINES_IMAGE_DIR.exists():
    MEDICINES_IMAGE_DIR = Path(settings.BASE_DIR).parent / 'Medicines'
BACKEND_PUBLIC_IMAGES = Path(settings.BASE_DIR).parent / 'backend' / 'public' / 'images'

def api_root_view(request):
    return JsonResponse({
        'status': 'healthy',
        'message': 'Wisdom Pharma Django REST API is live and operational.',
        'frontend_app': 'http://localhost:5173/',
        'admin_panel': 'http://127.0.0.1:8000/admin/',
        'syllabus_portal': 'http://127.0.0.1:8000/portal/',
        'endpoints': {
            'auth': '/api/auth/',
            'medicines': '/api/medicines/',
            'categories': '/api/categories/',
            'cart': '/api/cart/',
            'orders': '/api/orders/',
            'prescriptions': '/api/prescriptions/',
            'notifications': '/api/notifications/',
            'chatbot': '/api/chatbot/',
            'admin': '/api/admin/',
            'contact': '/api/contact/',
            'site_content': '/api/site-content/',
        }
    })

def root_view(request):
    return JsonResponse({
        'name': 'Wisdom Pharma Backend (Django 5)',
        'frontend_url': 'http://localhost:5173/',
        'api_url': 'http://127.0.0.1:8000/api/',
        'django_admin': 'http://127.0.0.1:8000/admin/',
        'int253_syllabus_portal': 'http://127.0.0.1:8000/portal/',
    })

urlpatterns = [
    # Static Medicine Images (Served for React Frontend)
    re_path(r'^images/medicines/(?P<path>.*)$', serve, {'document_root': MEDICINES_IMAGE_DIR}),
    re_path(r'^images/(?P<path>.*)$', serve, {'document_root': BACKEND_PUBLIC_IMAGES}),

    # Root & API Info
    path('', root_view, name='root'),
    path('api/', api_root_view, name='api_root'),

    # Django Admin (Unit V)
    path('admin/', admin.site.urls),

    # Web Pages & Templates (Unit II, III, IV, VI)
    path('portal/', include('apps.web.urls')),

    # REST APIs (for React Frontend & Mobile)
    path('api/auth/', include('apps.authentication.urls')),
    path('api/medicines/', include('apps.medicines.urls')),
    path('api/categories/', include('apps.categories.urls')),
    path('api/cart/', include('apps.cart.urls')),
    path('api/orders/', include('apps.orders.urls')),
    path('api/prescriptions/', include('apps.prescriptions.urls')),
    path('api/notifications/', include('apps.notifications.urls')),
    path('api/chatbot/', include('apps.chatbot.urls')),
    path('api/admin/', include('apps.admin_panel.urls')),
    path('api/contact/', include('apps.contact.urls')),
    path('api/site-content/', include('apps.site_content.urls')),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
