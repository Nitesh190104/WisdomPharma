from django.utils import timezone
from django.core.mail import send_mail
from django.conf import settings
from rest_framework.views import APIView
from rest_framework.response import Response
from apps.authentication.permissions import IsAdminRole
from apps.authentication.models import User, Business
from apps.medicines.models import Medicine
from apps.medicines.serializers import MedicineSerializer
from apps.categories.models import Category
from apps.categories.serializers import CategorySerializer
from apps.orders.models import Order
from apps.orders.serializers import OrderSerializer
from apps.prescriptions.models import Prescription
from apps.prescriptions.serializers import PrescriptionSerializer
from apps.site_content.models import SiteContent
from apps.site_content.serializers import SiteContentSerializer


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _paginate(queryset, request, serializer_class=None, transform_fn=None, **serializer_kwargs):
    page = int(request.query_params.get('page', 1))
    per_page = int(request.query_params.get('per_page', 15))
    total = queryset.count()
    start = (page - 1) * per_page
    end = start + per_page
    items_qs = queryset[start:end]
    if serializer_class:
        serialized = serializer_class(items_qs, many=True, **serializer_kwargs).data
    elif transform_fn:
        serialized = [transform_fn(i) for i in items_qs]
    else:
        serialized = list(items_qs)

    last_page = max(1, (total + per_page - 1) // per_page)
    return {
        'data': serialized,
        'items': serialized,
        'total': total,
        'current_page': page,
        'page': page,
        'per_page': per_page,
        'last_page': last_page,
        'total_pages': last_page,
    }


import threading

def _send(subject, body, recipient):
    def _task():
        try:
            send_mail(
                subject=subject,
                message=body,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[recipient],
                fail_silently=True,
            )
        except Exception:
            pass
    threading.Thread(target=_task, daemon=True).start()


# ---------------------------------------------------------------------------
# Dashboard
# ---------------------------------------------------------------------------

class AdminDashboardView(APIView):
    permission_classes = [IsAdminRole]

    def get(self, request):
        from django.db.models import Sum
        now = timezone.now()
        delivered_like = ['delivered', 'return_requested']

        total_rev = Order.objects.filter(status__in=delivered_like).aggregate(Sum('total'))['total__sum'] or 0.0
        if total_rev == 0.0:
            total_rev = Order.objects.filter(payment_status='paid').aggregate(Sum('total'))['total__sum'] or 0.0

        start_of_month = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        monthly_rev = Order.objects.filter(
            status__in=delivered_like,
            created_at__gte=start_of_month
        ).aggregate(Sum('total'))['total__sum'] or 0.0

        total_orders = Order.objects.count()
        processing_orders = Order.objects.filter(status='processing').count()
        delivered_orders = Order.objects.filter(status__in=delivered_like).count()

        total_users = User.objects.count()
        total_consumers = User.objects.filter(role='consumer').count()
        total_stores = User.objects.filter(role='store').count()
        pending_approvals = User.objects.filter(role='store', is_approved=False).count()

        total_medicines = Medicine.objects.filter(is_active=True).count()
        low_stock_medicines = Medicine.objects.filter(stock__lte=10, stock__gt=0, is_active=True).count()
        out_of_stock_medicines = Medicine.objects.filter(stock=0, is_active=True).count()

        recent_qs = Order.objects.select_related('user').order_by('-created_at')[:10]
        recent_orders = [
            {
                'id': o.id,
                '_id': o.id,
                'order_number': o.order_number,
                'customer': f"{o.user.first_name} {o.user.last_name}".strip() or o.user.email if o.user else 'N/A',
                'total': float(o.total),
                'status': o.status,
                'type': o.type,
                'created_at': o.created_at.strftime('%b %d, %Y %H:%M') if o.created_at else '',
            }
            for o in recent_qs
        ]

        revenue_chart = []
        for i in range(5, -1, -1):
            year = now.year
            month = now.month - i
            while month <= 0:
                month += 12
                year -= 1
            m_start = timezone.datetime(year, month, 1, tzinfo=timezone.get_current_timezone())
            if month == 12:
                m_end = timezone.datetime(year + 1, 1, 1, tzinfo=timezone.get_current_timezone())
            else:
                m_end = timezone.datetime(year, month + 1, 1, tzinfo=timezone.get_current_timezone())

            m_sum = Order.objects.filter(
                status__in=delivered_like,
                created_at__gte=m_start,
                created_at__lt=m_end
            ).aggregate(Sum('total'))['total__sum'] or 0.0

            revenue_chart.append({
                'month': m_start.strftime('%b %Y'),
                'revenue': round(float(m_sum), 2),
            })

        order_stats = [
            {'name': 'Processing', 'value': Order.objects.filter(status='processing').count()},
            {'name': 'Confirmed', 'value': Order.objects.filter(status='confirmed').count()},
            {'name': 'Shipped', 'value': Order.objects.filter(status='shipped').count()},
            {'name': 'Delivered', 'value': Order.objects.filter(status__in=delivered_like).count()},
            {'name': 'Cancelled', 'value': Order.objects.filter(status='cancelled').count()},
            {'name': 'Returned', 'value': Order.objects.filter(status='returned').count()},
        ]

        dashboard_data = {
            'revenue': {
                'total': round(float(total_rev), 2),
                'monthly': round(float(monthly_rev), 2),
                'chart': revenue_chart,
            },
            'orders': {
                'total': total_orders,
                'pending': 0,
                'processing': processing_orders,
                'delivered': delivered_orders,
                'stats': order_stats,
            },
            'users': {
                'total': total_users,
                'consumers': total_consumers,
                'stores': total_stores,
                'pending_approvals': pending_approvals,
            },
            'inventory': {
                'total_medicines': total_medicines,
                'low_stock': low_stock_medicines,
                'out_of_stock': out_of_stock_medicines,
            },
            'recent_orders': recent_orders,
        }

        return Response({
            'success': True,
            'data': dashboard_data,
            'message': 'Dashboard stats retrieved',
        })


# ---------------------------------------------------------------------------
# Users
# ---------------------------------------------------------------------------

class AdminUsersView(APIView):
    permission_classes = [IsAdminRole]

    def get(self, request):
        from django.db.models import Q
        users = User.objects.exclude(role='admin').order_by('-date_joined')
        search = request.query_params.get('search')
        if search:
            users = users.filter(
                Q(first_name__icontains=search) |
                Q(last_name__icontains=search) |
                Q(email__icontains=search) |
                Q(phone__icontains=search)
            )
        role = request.query_params.get('role')
        if role:
            users = users.filter(role=role)

        def transform_user(u):
            return {
                'id': u.id,
                '_id': u.id,
                'name': f"{u.first_name} {u.last_name}".strip() or u.email,
                'email': u.email,
                'first_name': u.first_name,
                'last_name': u.last_name,
                'phone': u.phone,
                'role': u.role,
                'is_active': u.is_active,
                'is_approved': u.is_approved,
                'created_at': u.date_joined.isoformat() if u.date_joined else '',
                'date_joined': u.date_joined.isoformat() if u.date_joined else '',
            }

        paged = _paginate(users, request, transform_fn=transform_user)
        return Response({
            'success': True,
            'data': paged,
            'message': 'Users retrieved',
        })


class AdminUserDetailView(APIView):
    permission_classes = [IsAdminRole]

    def put(self, request, pk):
        try:
            user = User.objects.get(pk=pk)
        except User.DoesNotExist:
            return Response({'success': False, 'message': 'User not found'}, status=404)

        allowed = {'is_active', 'is_approved', 'role'}
        for field in allowed:
            if field in request.data:
                setattr(user, field, request.data[field])
        user.save()
        return Response({
            'success': True,
            'data': {
                'id': user.id,
                'email': user.email,
                'is_active': user.is_active,
                'is_approved': user.is_approved,
                'role': user.role,
            },
            'message': 'User updated successfully',
        })


# ---------------------------------------------------------------------------
# Businesses
# ---------------------------------------------------------------------------

class PendingBusinessesView(APIView):
    permission_classes = [IsAdminRole]

    def get(self, request):
        businesses = Business.objects.filter(is_verified=False).order_by('-created_at')
        data = [
            {
                'id': b.id,
                'business_name': b.business_name,
                'gst_number': b.gst_number,
                'drug_license_number': b.drug_license_number,
                'is_verified': b.is_verified,
                'user': {
                    'id': b.user.id,
                    'email': b.user.email,
                    'first_name': b.user.first_name,
                    'last_name': b.user.last_name,
                    'phone': b.user.phone,
                },
                'created_at': b.created_at,
            }
            for b in businesses
        ]
        return Response({'success': True, 'data': data, 'message': 'Pending businesses retrieved'})


class ApproveBusinessView(APIView):
    permission_classes = [IsAdminRole]

    def post(self, request, pk):
        try:
            business = Business.objects.get(pk=pk)
        except Business.DoesNotExist:
            return Response({'success': False, 'message': 'Business not found'}, status=404)

        business.is_verified = True
        business.save()
        business.user.is_approved = True
        business.user.save()

        _send(
            subject='Your Wisdom Pharma business account has been approved',
            body=(
                f"Dear {business.user.first_name or business.user.email},\n\n"
                f"Congratulations! Your business '{business.business_name}' has been approved. "
                "You can now log in and start using the platform.\n\n"
                "— Wisdom Pharma Team"
            ),
            recipient=business.user.email,
        )

        return Response({'success': True, 'data': None, 'message': 'Business approved'})


class RejectBusinessView(APIView):
    permission_classes = [IsAdminRole]

    def post(self, request, pk):
        try:
            business = Business.objects.get(pk=pk)
        except Business.DoesNotExist:
            return Response({'success': False, 'message': 'Business not found'}, status=404)

        business.user.is_active = False
        business.user.save()

        reason = request.data.get('reason', '')
        _send(
            subject='Your Wisdom Pharma business application was not approved',
            body=(
                f"Dear {business.user.first_name or business.user.email},\n\n"
                f"We regret to inform you that your business application for '{business.business_name}' "
                f"has not been approved at this time.\n"
                f"{('Reason: ' + reason) if reason else ''}\n\n"
                "Please contact support for further assistance.\n\n"
                "— Wisdom Pharma Team"
            ),
            recipient=business.user.email,
        )

        return Response({'success': True, 'data': None, 'message': 'Business rejected'})


# ---------------------------------------------------------------------------
# Orders
# ---------------------------------------------------------------------------

class AdminOrdersView(APIView):
    permission_classes = [IsAdminRole]

    def get(self, request):
        qs = Order.objects.select_related('user').order_by('-created_at')
        status_filter = request.query_params.get('status')
        if status_filter:
            qs = qs.filter(status=status_filter)
        type_filter = request.query_params.get('type')
        if type_filter:
            qs = qs.filter(type=type_filter)
        paged = _paginate(qs, request, OrderSerializer)
        return Response({'success': True, 'data': paged, 'message': 'Orders retrieved'})


class UpdateOrderStatusView(APIView):
    permission_classes = [IsAdminRole]

    def put(self, request, pk):
        try:
            order = Order.objects.get(pk=pk)
        except Order.DoesNotExist:
            return Response({'success': False, 'message': 'Order not found'}, status=404)

        new_status = request.data.get('status')
        if not new_status:
            return Response({'success': False, 'message': 'status is required'}, status=400)

        order.status = new_status
        if new_status == 'delivered':
            order.delivered_at = timezone.now()
        elif new_status == 'cancelled':
            order.cancelled_at = timezone.now()
            order.cancellation_reason = request.data.get('cancellation_reason', '')
        order.save()

        _send(
            subject=f'Your Wisdom Pharma order {order.order_number} status update',
            body=(
                f"Dear {order.user.first_name or order.user.email},\n\n"
                f"Your order {order.order_number} status has been updated to: {new_status}.\n\n"
                "— Wisdom Pharma Team"
            ),
            recipient=order.user.email,
        )

        serializer = OrderSerializer(order)
        return Response({'success': True, 'data': serializer.data, 'message': 'Order status updated'})


class ApproveReturnView(APIView):
    permission_classes = [IsAdminRole]

    def post(self, request, pk):
        try:
            order = Order.objects.get(pk=pk)
        except Order.DoesNotExist:
            return Response({'success': False, 'message': 'Order not found'}, status=404)

        order.status = 'returned'
        order.returned_at = timezone.now()
        order.return_reviewed_at = timezone.now()
        order.return_reviewed_by = request.user.id
        order.save()

        _send(
            subject=f'Return approved for order {order.order_number}',
            body=(
                f"Dear {order.user.first_name or order.user.email},\n\n"
                f"Your return request for order {order.order_number} has been approved. "
                "A refund will be processed shortly.\n\n"
                "— Wisdom Pharma Team"
            ),
            recipient=order.user.email,
        )

        serializer = OrderSerializer(order)
        return Response({'success': True, 'data': serializer.data, 'message': 'Return approved'})


class RejectReturnView(APIView):
    permission_classes = [IsAdminRole]

    def post(self, request, pk):
        try:
            order = Order.objects.get(pk=pk)
        except Order.DoesNotExist:
            return Response({'success': False, 'message': 'Order not found'}, status=404)

        reject_reason = request.data.get('return_reject_reason', '')
        order.return_reject_reason = reject_reason
        order.return_reviewed_at = timezone.now()
        order.return_reviewed_by = request.user.id
        order.status = 'delivered'  # revert
        order.save()

        _send(
            subject=f'Return request rejected for order {order.order_number}',
            body=(
                f"Dear {order.user.first_name or order.user.email},\n\n"
                f"Your return request for order {order.order_number} has been rejected.\n"
                f"{('Reason: ' + reject_reason) if reject_reason else ''}\n\n"
                "— Wisdom Pharma Team"
            ),
            recipient=order.user.email,
        )

        serializer = OrderSerializer(order)
        return Response({'success': True, 'data': serializer.data, 'message': 'Return rejected'})


# ---------------------------------------------------------------------------
# Inventory
# ---------------------------------------------------------------------------

class InventoryView(APIView):
    permission_classes = [IsAdminRole]

    def get(self, request):
        from django.db.models import Q
        medicines = Medicine.objects.filter(is_active=True).select_related('category').order_by('medicine_name')
        search = request.query_params.get('search')
        if search:
            medicines = medicines.filter(
                Q(medicine_name__icontains=search) | Q(manufacturer__icontains=search)
            )
        low_stock = request.query_params.get('low_stock')
        if low_stock and str(low_stock).lower() in ['true', '1']:
            medicines = medicines.filter(stock__lte=10, stock__gt=0)
        out_of_stock = request.query_params.get('out_of_stock')
        if out_of_stock and str(out_of_stock).lower() in ['true', '1']:
            medicines = medicines.filter(stock=0)

        def transform_med(m):
            img_url = m.image or ''
            if img_url and not img_url.startswith('http'):
                img_url = request.build_absolute_uri(f"/images/medicines/{img_url.split('/')[-1]}")
            return {
                'id': m.id,
                '_id': m.id,
                'medicine_name': m.medicine_name,
                'description': m.description,
                'category': m.category.name if m.category else 'General',
                'category_id': m.category.id if m.category else None,
                'manufacturer': m.manufacturer,
                'stock': m.stock,
                'retail_price': m.retail_price,
                'wholesale_price': m.wholesale_price,
                'gst_percentage': m.gst_percentage,
                'is_low_stock': m.stock <= 10,
                'image': img_url,
                'is_active': m.is_active,
                'prescription_required': m.prescription_required,
                'dosage': m.dosage,
            }

        paged = _paginate(medicines, request, transform_fn=transform_med)
        return Response({'success': True, 'data': paged, 'message': 'Inventory retrieved'})


class UpdateStockView(APIView):
    permission_classes = [IsAdminRole]

    def put(self, request, pk):
        try:
            medicine = Medicine.objects.get(pk=pk)
        except Medicine.DoesNotExist:
            return Response({'success': False, 'message': 'Medicine not found'}, status=404)

        stock = request.data.get('stock')
        if stock is None:
            return Response({'success': False, 'message': 'stock is required'}, status=400)

        try:
            medicine.stock = int(stock)
        except (ValueError, TypeError):
            return Response({'success': False, 'message': 'stock must be an integer'}, status=400)

        medicine.save()
        serializer = MedicineSerializer(medicine)
        return Response({'success': True, 'data': serializer.data, 'message': 'Stock updated'})


# ---------------------------------------------------------------------------
# Prescriptions (admin)
# ---------------------------------------------------------------------------

class AdminPrescriptionsView(APIView):
    permission_classes = [IsAdminRole]

    def get(self, request):
        prescriptions = Prescription.objects.select_related('user').order_by('-created_at')
        status_filter = request.query_params.get('status')
        if status_filter:
            prescriptions = prescriptions.filter(status=status_filter)
        paged = _paginate(prescriptions, request, PrescriptionSerializer, context={'request': request})
        return Response({'success': True, 'data': paged, 'message': 'Prescriptions retrieved'})


class ReviewPrescriptionView(APIView):
    permission_classes = [IsAdminRole]

    def put(self, request, pk):
        try:
            prescription = Prescription.objects.get(pk=pk)
        except Prescription.DoesNotExist:
            return Response({'success': False, 'message': 'Prescription not found'}, status=404)

        new_status = request.data.get('status')
        if new_status not in ('approved', 'rejected'):
            return Response({'success': False, 'message': 'status must be approved or rejected'}, status=400)

        prescription.status = new_status
        prescription.review_notes = request.data.get('review_notes', '')
        prescription.reviewed_by = request.user.id
        prescription.reviewed_at = timezone.now()
        prescription.save()

        serializer = PrescriptionSerializer(prescription, context={'request': request})
        return Response({'success': True, 'data': serializer.data, 'message': f'Prescription {new_status}'})


# ---------------------------------------------------------------------------
# Medicines (admin CRUD)
# ---------------------------------------------------------------------------

class AdminMedicineCreateView(APIView):
    permission_classes = [IsAdminRole]

    def post(self, request):
        serializer = MedicineSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({'success': True, 'data': serializer.data, 'message': 'Medicine created'}, status=201)
        return Response({'success': False, 'data': serializer.errors, 'message': 'Validation failed'}, status=400)


class AdminMedicineUpdateView(APIView):
    permission_classes = [IsAdminRole]

    def put(self, request, pk):
        try:
            medicine = Medicine.objects.get(pk=pk)
        except Medicine.DoesNotExist:
            return Response({'success': False, 'message': 'Medicine not found'}, status=404)
        serializer = MedicineSerializer(medicine, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response({'success': True, 'data': serializer.data, 'message': 'Medicine updated'})
        return Response({'success': False, 'data': serializer.errors, 'message': 'Validation failed'}, status=400)

    def delete(self, request, pk):
        try:
            medicine = Medicine.objects.get(pk=pk)
        except Medicine.DoesNotExist:
            return Response({'success': False, 'message': 'Medicine not found'}, status=404)
        medicine.is_active = False
        medicine.save()
        return Response({'success': True, 'data': None, 'message': 'Medicine deactivated'})


# ---------------------------------------------------------------------------
# Categories (admin CRUD)
# ---------------------------------------------------------------------------

class AdminCategoryCreateView(APIView):
    permission_classes = [IsAdminRole]

    def post(self, request):
        serializer = CategorySerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({'success': True, 'data': serializer.data, 'message': 'Category created'}, status=201)
        return Response({'success': False, 'data': serializer.errors, 'message': 'Validation failed'}, status=400)


class AdminCategoryUpdateView(APIView):
    permission_classes = [IsAdminRole]

    def put(self, request, pk):
        try:
            category = Category.objects.get(pk=pk)
        except Category.DoesNotExist:
            return Response({'success': False, 'message': 'Category not found'}, status=404)
        serializer = CategorySerializer(category, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response({'success': True, 'data': serializer.data, 'message': 'Category updated'})
        return Response({'success': False, 'data': serializer.errors, 'message': 'Validation failed'}, status=400)

    def delete(self, request, pk):
        try:
            category = Category.objects.get(pk=pk)
        except Category.DoesNotExist:
            return Response({'success': False, 'message': 'Category not found'}, status=404)
        category.is_active = False
        category.save()
        return Response({'success': True, 'data': None, 'message': 'Category deactivated'})


# ---------------------------------------------------------------------------
# Site Content (admin)
# ---------------------------------------------------------------------------

class AdminSiteContentView(APIView):
    permission_classes = [IsAdminRole]

    def get(self, request, key):
        try:
            content = SiteContent.objects.get(key=key)
        except SiteContent.DoesNotExist:
            return Response({'success': False, 'message': 'Content not found'}, status=404)
        serializer = SiteContentSerializer(content)
        return Response({'success': True, 'data': serializer.data, 'message': 'Content retrieved'})

    def put(self, request, key):
        content, _ = SiteContent.objects.get_or_create(key=key)
        serializer = SiteContentSerializer(content, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response({'success': True, 'data': serializer.data, 'message': 'Content updated'})
        return Response({'success': False, 'data': serializer.errors, 'message': 'Validation failed'}, status=400)
