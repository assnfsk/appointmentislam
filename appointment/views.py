# appointment/views.py
from django.shortcuts import render, redirect
from django.http import JsonResponse
from datetime import datetime, timedelta
from django.contrib.admin.views.decorators import staff_member_required
from .models import Clinic, Doctor, Appointment, AvailabilitySettings
from .forms import AppointmentForm

def get_available_times(clinic, date):
    settings = AvailabilitySettings.objects.get(clinic=clinic)
    
    # Check if date is in unavailable days
    if str(date.weekday()) in settings.unavailable_days.split(','):
        return []
    
    # Generate time slots
    times = []
    current_time = settings.start_time
    end_time = settings.end_time
    duration = timedelta(minutes=settings.appointment_duration)
    
    while current_time <= end_time:
        # Check if slot is already booked
        if not Appointment.objects.filter(
            clinic=clinic,
            appointment_date=date,
            appointment_time=current_time
        ).exists():
            times.append(current_time)
        current_time = (datetime.combine(date, current_time) + duration).time()
    
    return times

def book_appointment(request):
    if request.method == 'POST':
        form = AppointmentForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('appointment:thank_you')  # Updated this line
    else:
        form = AppointmentForm()
    
    return render(request, 'appointment/book_appointment.html', {'form': form})

def thank_you(request):
    return render(request, 'appointment/thank_you.html')

def get_doctors(request):
    clinic_id = request.GET.get('clinic_id')
    doctors = Doctor.objects.filter(clinic_id=clinic_id).values('id', 'name')
    return JsonResponse(list(doctors), safe=False)

def get_available_slots(request):
    clinic_id = request.GET.get('clinic_id')
    date_str = request.GET.get('date')
    date = datetime.strptime(date_str, '%Y-%m-%d').date()
    
    times = get_available_times(Clinic.objects.get(id=clinic_id), date)
    return JsonResponse([t.strftime('%H:%M') for t in times], safe=False)


def appointment_list(request):
    appointments = Appointment.objects.all()
    clinics = Clinic.objects.all()
    doctors = Doctor.objects.all()
    
    # Apply filters
    clinic = request.GET.get('clinic')
    doctor = request.GET.get('doctor')
    date = request.GET.get('date')
    
    if clinic:
        appointments = appointments.filter(clinic_id=clinic)
    if doctor:
        appointments = appointments.filter(doctor_id=doctor)
    if date:
        appointments = appointments.filter(appointment_date=date)
    
    # Sort by date and time
    appointments = appointments.order_by('appointment_date', 'appointment_time')
    
    # Format time to 12-hour format
    for appointment in appointments:
        appointment.formatted_time = appointment.appointment_time.strftime('%I:%M %p').lstrip('0')
    
    context = {
        'appointments': appointments,
        'clinics': clinics,
        'doctors': doctors,
    }
    
    return render(request, 'appointment/appointment_list.html', context)


def get_available_times(clinic, date):
    try:
        settings = AvailabilitySettings.objects.get(
            clinic=clinic,
            start_date__lte=date,
            end_date__gte=date
        )
        
        # Check if the day is available
        day_of_week = date.weekday()  # 0-6 (Monday-Sunday)
        if day_of_week in settings.unavailable_days:
            return []
        
        # Generate time slots
        times = []
        current_time = settings.start_time
        end_time = settings.end_time
        duration = timedelta(minutes=settings.appointment_duration)
        
        while current_time <= end_time:
            # Check if slot is already booked
            if not Appointment.objects.filter(
                clinic=clinic,
                appointment_date=date,
                appointment_time=current_time
            ).exists():
                times.append(current_time)
            current_time = (datetime.combine(date, current_time) + duration).time()
        
        return times
    except AvailabilitySettings.DoesNotExist:
        return []  # No settings found for this date range
    
    # appointment/views.py
def get_unavailable_days(request):
    clinic_id = request.GET.get('clinic_id')
    try:
        settings = AvailabilitySettings.objects.get(
            clinic_id=clinic_id,
            start_date__lte=datetime.now().date(),
            end_date__gte=datetime.now().date()
        )
        return JsonResponse({'unavailable_days': settings.unavailable_days})
    except AvailabilitySettings.DoesNotExist:
        return JsonResponse({'unavailable_days': []})
    

