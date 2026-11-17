from rest_framework import status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Category
from apps.authentication.permissions import IsAdminRole


def _category_data(cat, include_children=False):
    data = {
        'id': cat.id,
        'name': cat.name,
        'slug': cat.slug,
        'description': cat.description,
        'image': cat.image,
        'is_active': cat.is_active,
        'parent': cat.parent_id,
        'created_at': cat.created_at.isoformat(),
        'updated_at': cat.updated_at.isoformat(),
    }
    if include_children:
        data['children'] = [_category_data(c) for c in cat.children.filter(is_active=True)]
    return data


class CategoryListCreateView(APIView):
    def get_permissions(self):
        if self.request.method == 'GET':
            return [AllowAny()]
        return [IsAdminRole()]

    def get(self, request):
        categories = Category.objects.filter(is_active=True, parent=None)
        return Response({
            'success': True,
            'data': [_category_data(c, include_children=True) for c in categories],
        })

    def post(self, request):
        name = request.data.get('name', '').strip()
        if not name:
            return Response({'success': False, 'message': 'Name is required'}, status=400)

        from django.utils.text import slugify
        slug = request.data.get('slug') or slugify(name)
        if Category.objects.filter(slug=slug).exists():
            slug = f"{slug}-{Category.objects.count()}"

        parent_id = request.data.get('parent')
        parent = None
        if parent_id:
            try:
                parent = Category.objects.get(id=parent_id)
            except Category.DoesNotExist:
                return Response({'success': False, 'message': 'Parent category not found'}, status=404)

        cat = Category.objects.create(
            name=name,
            slug=slug,
            description=request.data.get('description', ''),
            image=request.data.get('image', ''),
            is_active=request.data.get('is_active', True),
            parent=parent,
        )

        return Response({'success': True, 'message': 'Category created', 'data': _category_data(cat)}, status=201)


class CategoryDetailView(APIView):
    def get_permissions(self):
        if self.request.method == 'GET':
            return [AllowAny()]
        return [IsAdminRole()]

    def _get_category(self, pk):
        try:
            return Category.objects.get(pk=pk)
        except Category.DoesNotExist:
            return None

    def get(self, request, pk):
        cat = self._get_category(pk)
        if not cat:
            return Response({'success': False, 'message': 'Category not found'}, status=404)
        return Response({'success': True, 'data': _category_data(cat, include_children=True)})

    def put(self, request, pk):
        cat = self._get_category(pk)
        if not cat:
            return Response({'success': False, 'message': 'Category not found'}, status=404)

        for field in ['name', 'description', 'image', 'is_active']:
            if field in request.data:
                setattr(cat, field, request.data[field])

        if 'slug' in request.data:
            cat.slug = request.data['slug']

        parent_id = request.data.get('parent')
        if parent_id is not None:
            if parent_id == '':
                cat.parent = None
            else:
                try:
                    cat.parent = Category.objects.get(id=parent_id)
                except Category.DoesNotExist:
                    return Response({'success': False, 'message': 'Parent category not found'}, status=404)

        cat.save()
        return Response({'success': True, 'message': 'Category updated', 'data': _category_data(cat)})

    def delete(self, request, pk):
        cat = self._get_category(pk)
        if not cat:
            return Response({'success': False, 'message': 'Category not found'}, status=404)
        cat.is_active = False
        cat.save()
        return Response({'success': True, 'message': 'Category deleted'})
