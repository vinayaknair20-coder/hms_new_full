from django.db import models
from admin_app.models import Doctor, Staff

class Patient(models.Model):
    BLOOD_GROUP_CHOICES = [
        ('A+', 'A+'),
        ('A-', 'A-'),
        ('B+', 'B+'),
        ('B-', 'B-'),
        ('O+', 'O+'),
        ('O-', 'O-'),
        ('AB+', 'AB+'),
        ('AB-', 'AB-'),
    ]

    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    dob = models.DateField()
    gender = models.CharField(max_length=10)
    phone = models.CharField(max_length=15)
    address = models.TextField()
    emergency_contact = models.CharField(max_length=15)
    medical_history = models.TextField(blank=True)
    blood_group = models.CharField(max_length=3, choices=BLOOD_GROUP_CHOICES, null=True, blank=True)

class Appointment(models.Model):
    STATUS_CHOICES = [
        ('Scheduled', 'Scheduled'),
        ('Completed', 'Completed'),
        ('Cancelled', 'Cancelled'),
    ]
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE)
    doctor = models.ForeignKey(Doctor, on_delete=models.CASCADE)
    receptionist = models.ForeignKey(Staff, on_delete=models.SET_NULL, null=True)
    date_time = models.DateTimeField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Scheduled')

class Billing(models.Model):
    appointment = models.ForeignKey(Appointment, on_delete=models.CASCADE)
    total_fee = models.DecimalField(max_digits=10, decimal_places=2)
    consultation_fee = models.DecimalField(max_digits=8, decimal_places=2)
    medicine_fee = models.DecimalField(max_digits=8, decimal_places=2)
    created_by = models.ForeignKey(Staff, on_delete=models.SET_NULL, null=True)
    timestamp = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        # derive consultation fee from the appointment's doctor
        try:
            self.consultation_fee = self.appointment.doctor.consultation_fee
        except Exception:
            # if no doctor or consultation fee, leave as provided or zero
            if not self.consultation_fee:
                self.consultation_fee = 0
        # total fee is consultation + medicine
        self.total_fee = (self.consultation_fee or 0) + (self.medicine_fee or 0)
        super().save(*args, **kwargs)
