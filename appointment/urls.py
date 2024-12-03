from django.urls import path
from . import views

app_name = 'appointment'

urlpatterns = [
    path('', views.book_appointment, name='book_appointment'),
    path('thank-you/', views.thank_you, name='thank_you'),
    path('appointments/', views.appointment_list, name='appointment_list'),
    path('api/get-doctors/', views.get_doctors, name='get_doctors'),
    path('api/get-available-slots/', views.get_available_slots, name='get_available_slots'),
    path('api/get-unavailable-days/', views.get_unavailable_days, name='get_unavailable_days'),
]