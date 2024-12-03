# appointment/forms.py
from django import forms
from .models import Appointment, Doctor

class AppointmentForm(forms.ModelForm):
    class Meta:
        model = Appointment
        fields = ['clinic', 'doctor', 'patient_name', 'patient_phone', 'appointment_date', 'appointment_time']
        widgets = {
            'clinic': forms.Select(attrs={'class': 'form-control'}),
            'doctor': forms.Select(attrs={'class': 'form-control'}),
            'patient_name': forms.TextInput(attrs={'class': 'form-control'}),
            'patient_phone': forms.TextInput(attrs={'class': 'form-control'}),
            'appointment_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'appointment_time': forms.Select(attrs={'class': 'form-control'}),
        }

    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['doctor'].queryset = Doctor.objects.none()

        if 'clinic' in self.data:
            try:
                clinic_id = int(self.data.get('clinic'))
                self.fields['doctor'].queryset = Doctor.objects.filter(clinic_id=clinic_id)
            except (ValueError, TypeError):
                pass
        elif self.instance.pk:
            self.fields['doctor'].queryset = self.instance.clinic.doctors.all()