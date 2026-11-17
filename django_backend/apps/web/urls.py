from django.urls import path
from . import views

urlpatterns = [
    # Unit II: Views and URLs mapping
    path('', views.home_view, name='web_home'),
    path('medicines/', views.medicine_list_view, name='web_medicines'),
    path('medicines/<int:pk>/', views.medicine_detail_view, name='web_medicine_detail'),
    path('contact/', views.contact_view, name='web_contact'),
    path('login/', views.login_view, name='web_login'),
    path('logout/', views.logout_view, name='web_logout'),
    path('register/', views.register_view, name='web_register'),
    path('profile/', views.profile_view, name='web_profile'),
]
