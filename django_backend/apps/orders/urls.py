from django.urls import path
from . import views

urlpatterns = [
    path('', views.order_list_or_create, name='order-list-create'),
    path('<int:pk>/', views.order_detail, name='order-detail'),
    path('<int:pk>/cancel/', views.order_cancel, name='order-cancel'),
    path('<int:pk>/return/', views.order_return_request, name='order-return'),
]
