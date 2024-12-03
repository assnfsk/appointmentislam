# appointment/models.py
from django.db import models
from django.core.validators import RegexValidator
from django.core.exceptions import ValidationError

class Clinic(models.Model):
    name = models.CharField(max_length=100)
    
    def __str__(self):
        return self.name

class Doctor(models.Model):
    name = models.CharField(max_length=100)
    clinic = models.ForeignKey(Clinic, on_delete=models.CASCADE, related_name='doctors')
    
    def __str__(self):
        return f"{self.name} - {self.clinic.name}"

class AvailabilitySettings(models.Model):
    DAYS_OF_WEEK = [
        (0, 'Monday'),
        (1, 'Tuesday'),
        (2, 'Wednesday'),
        (3, 'Thursday'),
        (4, 'Friday'),
        (5, 'Saturday'),
        (6, 'Sunday'),
    ]

    clinic = models.ForeignKey(Clinic, on_delete=models.CASCADE)
    start_date = models.DateField()
    end_date = models.DateField()
    start_time = models.TimeField()
    end_time = models.TimeField()
    appointment_duration = models.IntegerField(help_text="Duration in minutes")
    
    # Individual fields for each day
    monday_available = models.BooleanField(default=True, verbose_name="Monday Available")
    tuesday_available = models.BooleanField(default=True, verbose_name="Tuesday Available")
    wednesday_available = models.BooleanField(default=True, verbose_name="Wednesday Available")
    thursday_available = models.BooleanField(default=True, verbose_name="Thursday Available")
    friday_available = models.BooleanField(default=True, verbose_name="Friday Available")
    saturday_available = models.BooleanField(default=False, verbose_name="Saturday Available")
    sunday_available = models.BooleanField(default=False, verbose_name="Sunday Available")

    def __str__(self):
        return f"{self.clinic.name} - {self.start_date} to {self.end_date}"

    def clean(self):
        if self.start_date and self.end_date and self.start_date > self.end_date:
            raise ValidationError("End date must be after start date")
        if self.start_time and self.end_time and self.start_time >= self.end_time:
            raise ValidationError("End time must be after start time")
        if self.appointment_duration <= 0:
            raise ValidationError("Appointment duration must be positive")

    @property
    def unavailable_days(self):
        """Returns a list of unavailable day numbers (0-6, Monday-Sunday)"""
        unavailable = []
        if not self.monday_available: unavailable.append(0)
        if not self.tuesday_available: unavailable.append(1)
        if not self.wednesday_available: unavailable.append(2)
        if not self.thursday_available: unavailable.append(3)
        if not self.friday_available: unavailable.append(4)
        if not self.saturday_available: unavailable.append(5)
        if not self.sunday_available: unavailable.append(6)
        return unavailable

class Appointment(models.Model):
    clinic = models.ForeignKey(Clinic, on_delete=models.CASCADE)
    doctor = models.ForeignKey(Doctor, on_delete=models.CASCADE)
    patient_name = models.CharField(max_length=100)
    phone_regex = RegexValidator(regex=r'^5\d{8}$', message="Phone number must start with 5 and be 9 digits")
    patient_phone = models.CharField(validators=[phone_regex], max_length=9)
    appointment_date = models.DateField()
    appointment_time = models.TimeField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.patient_name} - {self.doctor.name} - {self.appointment_date}"