from django.urls import path
from . import views

urlpatterns = [
    path('', views.PrescriptionListCreateView.as_view()),
]
