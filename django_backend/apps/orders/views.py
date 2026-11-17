import uuid
import datetime
from django.utils import timezone
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from .models import Order
from .serializers import OrderSerializer
from apps.cart.views import _get_cart_data
from apps.cart.models import Cart, CartItem
from apps.medicines.models import Medicine
from apps.notifications.models import Notification


def _generate_order_number():
    return f"WP-{uuid.uuid4().hex[:8].upper()}-{datetime.date.today().strftime('%Y%m%d')}"


@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def order_list_or_create(request):
    if request.method == 'GET':
        if getattr(request.user, 'role', '') == 'admin':
            orders = Order.objects.all().order_by('-created_at')
        else:
            orders = Order.objects.filter(user=request.user).order_by('-created_at')

        status_param = request.query_params.get('status')
        if status_param:
            orders = orders.filter(status=status_param)

        try:
            page = int(request.query_params.get('page', 1))
        except (ValueError, TypeError):
            page = 1
        try:
            per_page = int(request.query_params.get('per_page', 10))
        except (ValueError, TypeError):
            per_page = 10

        total = orders.count()
        total_pages = max(1, (total + per_page - 1) // per_page)
        start = (page - 1) * per_page
        end = start + per_page
        page_orders = orders[start:end]

        serialized_orders = OrderSerializer(page_orders, many=True).data
        for o in serialized_orders:
            o['_id'] = str(o['id'])

        return Response({
            'success': True,
            'data': {
                'data': serialized_orders,
                'current_page': page,
                'last_page': total_pages,
                'total': total,
            }
        })

    elif request.method == 'POST':
        # Create order from user's cart
        cart_data = _get_cart_data(request.user)
        items = cart_data.get('items', [])
        if not items:
            return Response({
                'success': False,
                'message': 'Cart is empty. Please add items before placing an order.'
            }, status=status.HTTP_422_UNPROCESSABLE_ENTITY)

        user_role = getattr(request.user, 'role', 'consumer')
        order_type = 'wholesale' if user_role == 'store' else 'retail'

        payment_method = request.data.get('payment_method', 'cod')
        is_upi = (payment_method == 'upi')

        order = Order.objects.create(
            user=request.user,
            order_number=_generate_order_number(),
            items=items,
            subtotal=cart_data['subtotal'],
            gst_total=cart_data['gst_total'],
            discount=0.0,
            total=cart_data['total'],
            status='processing',
            payment_status='paid' if is_upi else 'pending',
            payment_method=payment_method,
            razorpay_payment_id=request.data.get('razorpay_payment_id'),
            type=order_type,
            shipping_address=request.data.get('shipping_address', {}),
            billing_address=request.data.get('billing_address', {}),
            notes=request.data.get('notes', ''),
            estimated_delivery=(timezone.now() + datetime.timedelta(days=5)).date(),
        )

        # Deduct stock for each medicine
        for item in items:
            med_id = item.get('medicine_id')
            qty = item.get('quantity', 1)
            try:
                m = Medicine.objects.get(pk=med_id)
                m.stock = max(0, m.stock - qty)
                m.save()
            except Medicine.DoesNotExist:
                pass

        # Clear cart
        try:
            cart = Cart.objects.get(user=request.user)
            CartItem.objects.filter(cart=cart).delete()
        except Cart.DoesNotExist:
            pass

        # Create user notification
        try:
            Notification.objects.create(
                user=request.user,
                title='Order Placed Successfully',
                message=f"Your order #{order.order_number} has been placed. Total: ₹{order.total}",
                type='order',
                is_read=False,
                data={'order_id': order.id}
            )
        except Exception:
            pass

        serialized = OrderSerializer(order).data
        serialized['_id'] = str(order.id)

        return Response({
            'success': True,
            'message': 'Order placed successfully!',
            'data': serialized
        }, status=status.HTTP_201_CREATED)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def order_detail(request, pk):
    try:
        if getattr(request.user, 'role', '') == 'admin':
            order = Order.objects.get(pk=pk)
        else:
            order = Order.objects.get(pk=pk, user=request.user)
    except Order.DoesNotExist:
        return Response({'success': False, 'message': 'Order not found.'}, status=status.HTTP_404_NOT_FOUND)

    serialized = OrderSerializer(order).data
    serialized['_id'] = str(order.id)
    return Response({'success': True, 'data': serialized})


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def order_cancel(request, pk):
    try:
        order = Order.objects.get(pk=pk, user=request.user)
    except Order.DoesNotExist:
        return Response({'success': False, 'message': 'Order not found.'}, status=status.HTTP_404_NOT_FOUND)

    if order.status not in ('processing', 'confirmed', 'pending'):
        return Response({'success': False, 'message': 'This order cannot be cancelled.'}, status=status.HTTP_422_UNPROCESSABLE_ENTITY)

    # Restore stock
    for item in order.items or []:
        med_id = item.get('medicine_id')
        qty = item.get('quantity', 1)
        try:
            m = Medicine.objects.get(pk=med_id)
            m.stock += qty
            m.save()
        except Medicine.DoesNotExist:
            pass

    order.status = 'cancelled'
    order.cancelled_at = timezone.now()
    order.cancellation_reason = request.data.get('reason', 'Cancelled by user')
    order.save()

    return Response({'success': True, 'message': 'Order cancelled.'})


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def order_return_request(request, pk):
    try:
        order = Order.objects.get(pk=pk, user=request.user)
    except Order.DoesNotExist:
        return Response({'success': False, 'message': 'Order not found.'}, status=status.HTTP_404_NOT_FOUND)

    if order.status != 'delivered':
        return Response({'success': False, 'message': 'Only delivered orders can be returned.'}, status=status.HTTP_422_UNPROCESSABLE_ENTITY)

    reason = request.data.get('reason', '').strip()
    if not reason:
        return Response({'success': False, 'message': 'Reason is required.'}, status=status.HTTP_422_UNPROCESSABLE_ENTITY)

    order.status = 'return_requested'
    order.return_requested_at = timezone.now()
    order.return_reason = reason
    order.save()

    return Response({'success': True, 'message': 'Return request submitted. Awaiting admin approval.'})
