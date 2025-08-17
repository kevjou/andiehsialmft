from django.urls import path
from . import views

app_name = 'therapy'

urlpatterns = [
    path('', views.home, name='home'),
    path('faq/', views.faq, name='faq'),
    path('scheduling/', views.scheduling, name='scheduling'),
    path('submit-appointment/', views.submit_appointment, name='submit_appointment'),
]