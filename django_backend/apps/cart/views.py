import math
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from .models import Cart, CartItem
from apps.medicines.models import Medicine


def _get_cart_data(user):
    cart, _ = Cart.objects.get_or_create(user=user)
    price_type = 'wholesale' if getattr(user, 'role', '') == 'store' else 'retail'

    items_list = []
    subtotal = 0.0
    gst_total = 0.0

    # Retrieve all items in the cart through the ManyToMany relationship
    cart_items = cart.items.all().select_related('medicine')
    for item in cart_items:
        med = item.medicine
        if not med:
            continue

        unit_price = med.wholesale_price if price_type == 'wholesale' else med.retail_price
        gst_pct = med.gst_percentage or 0.0
        gst_amount = (unit_price * gst_pct / 100.0) * item.quantity
        item_subtotal = unit_price * item.quantity
        item_total = item_subtotal + gst_amount

        items_list.append({
            'medicine_id': med.id,
            'medicine_name': med.medicine_name,
            'image': med.image or '',
            'quantity': item.quantity,
            'unit_price': unit_price,
            'gst_percentage': gst_pct,
            'gst_amount': math.ceil(gst_amount),
            'subtotal': math.ceil(item_subtotal),
            'total': math.ceil(item_total),
            'price_type': price_type,
            'stock': med.stock,
            'prescription_required': med.prescription_required,
            'min_wholesale_qty': med.min_wholesale_qty or 1,
        })

        subtotal += item_subtotal
        gst_total += gst_amount

    return {
        'id': cart.id,
        'items': items_list,
        'item_count': len(items_list),
        'subtotal': math.ceil(subtotal),
        'gst_total': math.ceil(gst_total),
        'total': math.ceil(subtotal + gst_total),
    }


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def cart_detail(request):
    data = _get_cart_data(request.user)
    return Response({'success': True, 'data': data})


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def cart_add(request):
    medicine_id = request.data.get('medicine_id')
    try:
        quantity = int(request.data.get('quantity', 1))
    except (ValueError, TypeError):
        quantity = 1

    if not medicine_id:
        return Response({'success': False, 'message': 'medicine_id is required.'}, status=status.HTTP_400_BAD_REQUEST)

    try:
        medicine = Medicine.objects.get(pk=medicine_id, is_active=True)
    except Medicine.DoesNotExist:
        return Response({'success': False, 'message': 'Medicine not found.'}, status=status.HTTP_404_NOT_FOUND)

    if medicine.stock <= 0:
        return Response({'success': False, 'message': 'Medicine is out of stock.'}, status=status.HTTP_400_BAD_REQUEST)

    if quantity > medicine.stock:
        return Response({'success': False, 'message': f'Only {medicine.stock} units available.'}, status=status.HTTP_400_BAD_REQUEST)

    cart, _ = Cart.objects.get_or_create(user=request.user)
    item = cart.items.filter(medicine=medicine).first()
    if item:
        item.quantity += quantity
        item.save()
    else:
        item = CartItem.objects.create(medicine=medicine, quantity=quantity)
        cart.items.add(item)

    data = _get_cart_data(request.user)
    return Response({
        'success': True,
        'message': 'Item added to cart.',
        'data': data,
    })


@api_view(['PUT', 'POST'])
@permission_classes([IsAuthenticated])
def cart_update_item(request):
    medicine_id = request.data.get('medicine_id')
    try:
        quantity = int(request.data.get('quantity', 1))
    except (ValueError, TypeError):
        quantity = 1

    if not medicine_id:
        return Response({'success': False, 'message': 'medicine_id is required.'}, status=status.HTTP_400_BAD_REQUEST)

    cart, _ = Cart.objects.get_or_create(user=request.user)
    item = cart.items.filter(medicine_id=medicine_id).first()
    if not item:
        return Response({'success': False, 'message': 'Cart item not found.'}, status=status.HTTP_404_NOT_FOUND)

    if quantity <= 0:
        cart.items.remove(item)
        item.delete()
        data = _get_cart_data(request.user)
        return Response({'success': True, 'message': 'Item removed from cart.', 'data': data})

    if quantity > item.medicine.stock:
        return Response({'success': False, 'message': f'Only {item.medicine.stock} units available.'}, status=status.HTTP_400_BAD_REQUEST)

    item.quantity = quantity
    item.save()

    data = _get_cart_data(request.user)
    return Response({'success': True, 'message': 'Cart updated.', 'data': data})


@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def cart_remove_item(request, medicine_id):
    cart, _ = Cart.objects.get_or_create(user=request.user)
    item = cart.items.filter(medicine_id=medicine_id).first()
    if item:
        cart.items.remove(item)
        item.delete()
    data = _get_cart_data(request.user)
    return Response({'success': True, 'message': 'Item removed from cart.', 'data': data})


@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def cart_clear(request):
    cart, _ = Cart.objects.get_or_create(user=request.user)
    for item in cart.items.all():
        item.delete()
    cart.items.clear()
    return Response({
        'success': True,
        'message': 'Cart cleared.',
        'data': {
            'items': [],
            'item_count': 0,
            'subtotal': 0,
            'gst_total': 0,
            'total': 0,
        }
    })
