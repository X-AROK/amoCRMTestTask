from django.urls import path
from . import views

urlpatterns = [
    path('', views.auth),
    path('contacts/', views.contacts),
]
