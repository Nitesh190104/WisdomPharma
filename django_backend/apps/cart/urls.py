from django.urls import path
from . import views

urlpatterns = [
    path('', views.cart_detail, name='cart-detail'),
    path('add/', views.cart_add, name='cart-add'),
    path('update/', views.cart_update_item, name='cart-update-item'),
    path('remove/<int:medicine_id>/', views.cart_remove_item, name='cart-remove-item'),
    path('clear/', views.cart_clear, name='cart-clear'),
]
