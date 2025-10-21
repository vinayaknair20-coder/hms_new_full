from django.db import models
from admin_app.models import Doctor
from receptionist_app.models import Patient, Appointment

class Consultation(models.Model):
    appointment = models.OneToOneField(Appointment, on_delete=models.CASCADE)
    doctor = models.ForeignKey(Doctor, on_delete=models.CASCADE)
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE)
    symptoms = models.TextField(null= True)
    diagnosis = models.TextField(null= True)
    notes = models.TextField(blank=True)
    date_time = models.DateTimeField(auto_now_add=True)

class Prescription(models.Model):
    consultation = models.OneToOneField(Consultation, on_delete=models.CASCADE)
    doctor = models.ForeignKey(Doctor, on_delete=models.CASCADE)
    dosage = models.CharField(max_length=100, null= True)
    frequency = models.CharField(max_length=100, null= True)
    duration = models.CharField(max_length=100, null= True)
    prescription_notes = models.TextField(blank=True)
    date_time = models.DateTimeField(auto_now_add=True)
