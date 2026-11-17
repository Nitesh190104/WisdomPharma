import os
import random

from django.conf import settings
from django.db.models import Q
from django.utils import timezone

from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Medicine
from apps.authentication.permissions import IsAdminRole


def _medicine_data(med, request=None):
    category_name = med.category.name if med.category else 'General'
    return {
        'id': med.id,
        '_id': str(med.id),
        'medicine_name': med.medicine_name,
        'description': med.description,
        'category': category_name,
        'category_id': med.category.id if med.category else None,
        'category_detail': {
            'id': med.category.id,
            'name': med.category.name,
            'slug': med.category.slug,
        } if med.category else None,
        'stock': med.stock,
        'retail_price': med.retail_price,
        'wholesale_price': med.wholesale_price,
        'retail_price_with_gst': med.retail_price_with_gst(),
        'wholesale_price_with_gst': med.wholesale_price_with_gst(),
        'gst_percentage': med.gst_percentage,
        'expiry_date': med.expiry_date.isoformat() if med.expiry_date else None,
        'manufacturer': med.manufacturer,
        'prescription_required': med.prescription_required,
        'image': med.image,
        'is_active': med.is_active,
        'min_wholesale_qty': med.min_wholesale_qty,
        'dosage': med.dosage,
        'composition': med.composition,
        'side_effects': med.side_effects,
        'usage_instructions': med.usage_instructions,
        'is_low_stock': med.is_low_stock(),
        'is_expired': med.is_expired(),
        'created_at': med.created_at.isoformat(),
        'updated_at': med.updated_at.isoformat(),
    }


class MedicineListView(APIView):
    permission_classes = [AllowAny]

    def get_permissions(self):
        if self.request.method in ('POST',):
            return [IsAdminRole()]
        return [AllowAny()]

    def get(self, request):
        qs = Medicine.objects.filter(is_active=True, deleted_at__isnull=True)

        # Filters
        search = request.query_params.get('search')
        if search:
            qs = qs.filter(
                Q(medicine_name__icontains=search) |
                Q(description__icontains=search) |
                Q(manufacturer__icontains=search) |
                Q(composition__icontains=search)
            )

        category_id = request.query_params.get('category_id') or request.query_params.get('category')
        if category_id:
            try:
                cat_int = int(category_id)
                qs = qs.filter(category_id=cat_int)
            except (ValueError, TypeError):
                qs = qs.filter(Q(category__name__iexact=category_id) | Q(category__slug__iexact=category_id))

        prescription_required = request.query_params.get('prescription_required')
        if prescription_required is not None:
            val = str(prescription_required).lower() in ('true', '1', 'yes')
            qs = qs.filter(prescription_required=val)

        min_price = request.query_params.get('min_price')
        if min_price:
            try:
                qs = qs.filter(retail_price__gte=float(min_price))
            except ValueError:
                pass

        max_price = request.query_params.get('max_price')
        if max_price:
            try:
                qs = qs.filter(retail_price__lte=float(max_price))
            except ValueError:
                pass

        in_stock = request.query_params.get('in_stock')
        if in_stock and str(in_stock).lower() in ('true', '1', 'yes'):
            qs = qs.filter(stock__gt=0)

        # Sorting
        sort_by = request.query_params.get('sort_by', 'created_at')
        sort_order = request.query_params.get('sort_order', 'desc')
        allowed_sort = ['medicine_name', 'retail_price', 'wholesale_price', 'stock', 'created_at']
        if sort_by not in allowed_sort:
            sort_by = 'created_at'
        if sort_order == 'desc':
            sort_by = f'-{sort_by}'
        qs = qs.order_by(sort_by)

        # Pagination
        try:
            per_page = int(request.query_params.get('per_page', 12))
        except (ValueError, TypeError):
            per_page = 12
        try:
            page = int(request.query_params.get('page', 1))
        except (ValueError, TypeError):
            page = 1

        total = qs.count()
        total_pages = max(1, (total + per_page - 1) // per_page)
        start = (page - 1) * per_page
        end = start + per_page
        medicines = qs[start:end]
        med_list = [_medicine_data(m, request) for m in medicines]

        return Response({
            'success': True,
            'data': {
                'data': med_list,
                'medicines': med_list,
                'current_page': page,
                'last_page': total_pages,
                'per_page': per_page,
                'total': total,
                'pagination': {
                    'total': total,
                    'page': page,
                    'per_page': per_page,
                    'total_pages': total_pages,
                }
            }
        })

    def post(self, request):
        name = request.data.get('medicine_name', '').strip()
        if not name:
            return Response({'success': False, 'message': 'Medicine name is required'}, status=400)

        image_url = ''
        image_file = request.FILES.get('image')
        if image_file:
            ext = image_file.name.rsplit('.', 1)[-1]
            safe_name = name.replace(' ', '_').lower()
            filename = f"{safe_name}.{ext}"
            upload_dir = os.path.join(settings.MEDIA_ROOT, 'medicines')
            os.makedirs(upload_dir, exist_ok=True)
            filepath = os.path.join(upload_dir, filename)
            with open(filepath, 'wb+') as f:
                for chunk in image_file.chunks():
                    f.write(chunk)
            image_url = f"{settings.MEDIA_URL}medicines/{filename}"

        from apps.categories.models import Category
        category = None
        category_id = request.data.get('category_id') or request.data.get('category')
        if category_id:
            try:
                category = Category.objects.get(id=category_id)
            except Category.DoesNotExist:
                pass

        med = Medicine.objects.create(
            medicine_name=name,
            description=request.data.get('description', ''),
            category=category,
            stock=int(request.data.get('stock', 0)),
            retail_price=float(request.data.get('retail_price', 0)),
            wholesale_price=float(request.data.get('wholesale_price', 0)),
            gst_percentage=float(request.data.get('gst_percentage', 0)),
            manufacturer=request.data.get('manufacturer', ''),
            prescription_required=str(request.data.get('prescription_required', 'false')).lower() in ('true', '1', 'yes'),
            image=image_url,
            is_active=True,
            min_wholesale_qty=int(request.data.get('min_wholesale_qty', 10)),
            dosage=request.data.get('dosage', ''),
            composition=request.data.get('composition', ''),
            side_effects=request.data.get('side_effects', ''),
            usage_instructions=request.data.get('usage_instructions', ''),
        )

        if request.data.get('expiry_date'):
            med.expiry_date = request.data['expiry_date']
            med.save()

        return Response({'success': True, 'message': 'Medicine created', 'data': _medicine_data(med, request)}, status=201)


class FeaturedMedicinesView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        qs = list(Medicine.objects.filter(is_active=True, deleted_at__isnull=True, stock__gt=0))
        featured = random.sample(qs, min(8, len(qs)))
        return Response({'success': True, 'data': [_medicine_data(m, request) for m in featured]})


class MedicineDetailView(APIView):
    def get_permissions(self):
        if self.request.method == 'GET':
            return [AllowAny()]
        return [IsAdminRole()]

    def _get_medicine(self, pk):
        try:
            return Medicine.objects.get(pk=pk, deleted_at__isnull=True)
        except Medicine.DoesNotExist:
            return None

    def get(self, request, pk):
        med = self._get_medicine(pk)
        if not med:
            return Response({'success': False, 'message': 'Medicine not found'}, status=404)
        return Response({'success': True, 'data': _medicine_data(med, request)})

    def put(self, request, pk):
        med = self._get_medicine(pk)
        if not med:
            return Response({'success': False, 'message': 'Medicine not found'}, status=404)

        simple_fields = [
            'medicine_name', 'description', 'stock', 'retail_price',
            'wholesale_price', 'gst_percentage', 'manufacturer',
            'min_wholesale_qty', 'dosage', 'composition',
            'side_effects', 'usage_instructions', 'expiry_date',
        ]
        for field in simple_fields:
            if field in request.data:
                setattr(med, field, request.data[field])

        if 'prescription_required' in request.data:
            med.prescription_required = str(request.data['prescription_required']).lower() in ('true', '1', 'yes')

        if 'is_active' in request.data:
            med.is_active = str(request.data['is_active']).lower() in ('true', '1', 'yes')

        # Category
        category_id = request.data.get('category_id') or request.data.get('category')
        if category_id:
            from apps.categories.models import Category
            try:
                med.category = Category.objects.get(id=category_id)
            except Category.DoesNotExist:
                pass

        # Image replacement
        image_file = request.FILES.get('image')
        if image_file:
            ext = image_file.name.rsplit('.', 1)[-1]
            safe_name = med.medicine_name.replace(' ', '_').lower()
            filename = f"{safe_name}.{ext}"
            upload_dir = os.path.join(settings.MEDIA_ROOT, 'medicines')
            os.makedirs(upload_dir, exist_ok=True)
            filepath = os.path.join(upload_dir, filename)
            with open(filepath, 'wb+') as f:
                for chunk in image_file.chunks():
                    f.write(chunk)
            med.image = f"{settings.MEDIA_URL}medicines/{filename}"

        med.save()
        return Response({'success': True, 'message': 'Medicine updated', 'data': _medicine_data(med, request)})

    def delete(self, request, pk):
        med = self._get_medicine(pk)
        if not med:
            return Response({'success': False, 'message': 'Medicine not found'}, status=404)
        med.deleted_at = timezone.now()
        med.is_active = False
        med.save()
        return Response({'success': True, 'message': 'Medicine deleted'})
