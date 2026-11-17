from django.urls import path
from . import views

urlpatterns = [
    path('', views.MedicineListView.as_view()),
    path('featured/', views.FeaturedMedicinesView.as_view()),
    path('<int:pk>/', views.MedicineDetailView.as_view()),
]
