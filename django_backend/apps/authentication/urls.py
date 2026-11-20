from django.urls import path
from . import views

urlpatterns = [
    path('send-otp/', views.SendOtpView.as_view()),
    path('verify-otp/', views.VerifyOtpView.as_view()),
    path('register/', views.RegisterView.as_view()),
    path('login/', views.LoginView.as_view()),
    path('profile/', views.ProfileView.as_view()),
    path('logout/', views.LogoutView.as_view()),
    path('test-email/', views.TestEmailView.as_view()),
]
