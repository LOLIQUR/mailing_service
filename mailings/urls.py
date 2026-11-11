from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('start/<int:pk>/', views.start_mailing, name='start_mailing'),
    path('stats/<int:pk>/', views.mailing_stats, name='mailing_stats'),
]
