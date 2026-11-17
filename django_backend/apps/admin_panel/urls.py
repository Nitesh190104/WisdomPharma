from django.urls import path
from . import views
from apps.chatbot.views import AdminChatbotView

urlpatterns = [
    path('dashboard/', views.AdminDashboardView.as_view(), name='admin_dashboard'),
    path('chatbot/message/', AdminChatbotView.as_view(), name='admin_chatbot_message'),
    path('users/', views.AdminUsersView.as_view(), name='admin_users'),
    path('users/<int:pk>/', views.AdminUserDetailView.as_view(), name='admin_user_detail'),
    path('businesses/pending/', views.PendingBusinessesView.as_view(), name='admin_pending_businesses'),
    path('businesses/<int:pk>/approve/', views.ApproveBusinessView.as_view(), name='admin_approve_business'),
    path('businesses/<int:pk>/reject/', views.RejectBusinessView.as_view(), name='admin_reject_business'),
    path('orders/', views.AdminOrdersView.as_view(), name='admin_orders'),
    path('orders/<int:pk>/status/', views.UpdateOrderStatusView.as_view(), name='admin_update_order_status'),
    path('orders/<int:pk>/return/approve/', views.ApproveReturnView.as_view(), name='admin_approve_return'),
    path('orders/<int:pk>/return/reject/', views.RejectReturnView.as_view(), name='admin_reject_return'),
    path('inventory/', views.InventoryView.as_view(), name='admin_inventory'),
    path('inventory/<int:pk>/stock/', views.UpdateStockView.as_view(), name='admin_update_stock'),
    path('prescriptions/', views.AdminPrescriptionsView.as_view(), name='admin_prescriptions'),
    path('prescriptions/<int:pk>/review/', views.ReviewPrescriptionView.as_view(), name='admin_review_prescription'),
    path('medicines/', views.AdminMedicineCreateView.as_view(), name='admin_medicine_create'),
    path('medicines/<int:pk>/', views.AdminMedicineUpdateView.as_view(), name='admin_medicine_update'),
    path('categories/', views.AdminCategoryCreateView.as_view(), name='admin_category_create'),
    path('categories/<int:pk>/', views.AdminCategoryUpdateView.as_view(), name='admin_category_update'),
    path('site-content/<str:key>/', views.AdminSiteContentView.as_view(), name='admin_site_content'),
]
