from django.db import models
from admin_app.models import Staff, Doctor

class Patient(models.Model):
    GENDER_CHOICES = [
        ('Male', 'Male'),
        ('Female', 'Female'),
        ('Other', 'Other'),
    ]

    BLOOD_GROUP_CHOICES = [
        ('A+', 'A+'), ('A-', 'A-'),
        ('B+', 'B+'), ('B-', 'B-'),
        ('O+', 'O+'), ('O-', 'O-'),
        ('AB+', 'AB+'), ('AB-', 'AB-'),
    ]

    Patient_name = models.CharField(max_length=100)
    dob = models.DateField(null=True, blank=True)
    gender = models.CharField(max_length=10, choices=GENDER_CHOICES)
    phone = models.CharField(max_length=15)
    address = models.TextField(null=True, blank=True)
    emergency_contact = models.CharField(max_length=15)
    blood_group = models.CharField(max_length=3, choices=BLOOD_GROUP_CHOICES, null=True, blank=True)

    def __str__(self):
        return f"{self.Patient_name} - (ID: {self.id})"


class Appointment(models.Model):
    Patient = models.ForeignKey(Patient, on_delete=models.CASCADE, default=1)
    doctor = models.ForeignKey(
        Doctor,
        on_delete=models.SET_NULL,
        related_name='appointments',
        null=True,
        blank=True
    )
    Appointment_date = models.DateField(null=True, blank=True)
    Appointment_time = models.TimeField(auto_now_add=True, null=True, blank=True)

    def __str__(self):
        doctor_name = self.doctor.user.username if self.doctor else "No Doctor Assigned"
        return f"Appointment {self.id} - {self.Patient.Patient_name} on {self.Appointment_date}"


class Bill_Generation(models.Model):
    Patient = models.ForeignKey(
        Patient, on_delete=models.CASCADE, related_name='bills', null=True, blank=True
    )
    Appointment = models.ForeignKey(
        Appointment, on_delete=models.CASCADE, related_name='bills', null=True, blank=True
    )

    registration_fee = models.DecimalField(max_digits=10, decimal_places=2, default=250)
    consultation_fee = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    Amount = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    Billing_date = models.DateField(auto_now_add=True)
    Token = models.CharField(max_length=20, unique=True, blank=True, null=True)

    def save(self, *args, **kwargs):
        # ⿡ Set consultation fee if doctor has it
        if self.Appointment and self.Appointment.doctor:
            self.consultation_fee = getattr(
                self.Appointment.doctor, 'consultation_fee', self.consultation_fee
            )

        # ⿢ Calculate total amount
        self.Amount = (self.registration_fee or 0) + (self.consultation_fee or 0)

        # ⿣ Generate unique Token if not present
        if not self.Token:
            last_bill = Bill_Generation.objects.order_by('-id').first()
            if last_bill and last_bill.Token and last_bill.Token.startswith("PAT"):
                try:
                    last_number = int(last_bill.Token.replace("PAT", ""))
                except ValueError:
                    last_number = 100
                new_number = last_number + 1
            else:
                new_number = 101
            self.Token = f"PAT{new_number}"

        super().save(*args, **kwargs)

    def __str__(self):
        patient_name = self.Patient.Patient_name if self.Patient else "Unknown"
        return f"Bill {self.id} - {patient_name} - Token: {self.Token}"
