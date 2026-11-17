import json
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from apps.authentication.permissions import IsAdminRole
from .models import SiteContent


class SiteContentView(APIView):
    def get_permissions(self):
        if self.request.method == 'GET':
            return [AllowAny()]
        return [IsAdminRole()]

    def get(self, request, key):
        try:
            content = SiteContent.objects.get(key=key)
            try:
                val = json.loads(content.value)
            except Exception:
                val = content.value
            return Response({'success': True, 'data': val})
        except SiteContent.DoesNotExist:
            return Response({'success': True, 'data': None})

    def put(self, request, key):
        data = request.data.get('data') if 'data' in request.data else request.data
        content, _ = SiteContent.objects.get_or_create(key=key)
        if isinstance(data, (dict, list)):
            content.value = json.dumps(data)
        else:
            content.value = str(data)
        content.save()
        return Response({
            'success': True,
            'message': 'Content updated successfully.',
            'data': data,
        })
