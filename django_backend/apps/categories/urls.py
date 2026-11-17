from django.urls import path
from . import views

urlpatterns = [
    path('', views.CategoryListCreateView.as_view()),
    path('<int:pk>/', views.CategoryDetailView.as_view()),
]
