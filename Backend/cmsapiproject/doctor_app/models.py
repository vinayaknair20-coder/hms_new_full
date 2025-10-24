from django.db import models
from django.utils import timezone
from admin_app.models import Staff
from receptionist_app.models import Appointment


# ✅ Define it locally
def get_today_date():
    return timezone.now().date()
def get_current_time():
    return timezone.now().time()




class Consultation(models.Model):
    STATUS_CHOICES = [
        ('SCHEDULED', 'Scheduled'),
        ('INPROGRESS', 'In Progress'),
        ('COMPLETED', 'Completed'),
        ('CANCELLED', 'Cancelled'),
    ]

    consultationid = models.AutoField(primary_key=True)
    appointment = models.OneToOneField(
        Appointment,
        on_delete=models.CASCADE,
        related_name='consultation',
        null=True,
        blank=True
    )
    doctor = models.ForeignKey(
        Staff,
        on_delete=models.CASCADE,
        related_name='consultations',
        null=True,
        blank=True
    )
    consultationdate = models.DateField(default=get_today_date)
    consultationtime = models.TimeField(default=get_current_time)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='SCHEDULED')
    symptoms = models.TextField(blank=True, null=True)
    diagnosis = models.TextField(blank=True, null=True)
    consultation_notes = models.TextField(blank=True, null=True)

    class Meta:
        db_table = 'doctor_app_consultations'
        ordering = ['-consultationdate']

    def _str_(self):
        patient_name = (
            self.appointment.Patient.Patient_name
            if self.appointment and self.appointment.Patient else "Unknown"
        )
        return f'Consultation {self.consultationid} - Patient: {patient_name}'



class Prescription(models.Model):
    prescriptionid = models.AutoField(primary_key=True)
    consultation = models.OneToOneField(Consultation, on_delete=models.CASCADE, related_name='prescriptions', null=True, blank=True)
    doctor = models.ForeignKey(Staff, on_delete=models.CASCADE, related_name='prescriptions', null=True, blank=True)
    prescriptiondate = models.DateField(default=get_today_date)
    general_instructions = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'doctor_app_prescription'
        ordering = ['-prescriptiondate']

    def _str_(self):
        return f'Prescription {self.prescriptionid}'

class MedicinePrescription(models.Model):
    prescription = models.ForeignKey(Prescription, on_delete=models.CASCADE, related_name='medicine_prescriptions')
    medicinename = models.CharField(max_length=200)
    dosage = models.CharField(max_length=100)
    frequency = models.CharField(max_length=100)
    timing = models.CharField(max_length=100)
    duration = models.CharField(max_length=100)
    quantity = models.PositiveIntegerField()

    class Meta:
        db_table = 'doctor_app_medicineprescriptions'

    def _str_(self):
        return f'Medicine {self.medicinename} for Prescription {self.prescription.prescriptionid}'

class TestPrescription(models.Model):
    prescription = models.ForeignKey(Prescription, on_delete=models.CASCADE, related_name='test_prescriptions')
    testname = models.CharField(max_length=200)
    instructions = models.TextField(blank=True, null=True)

    class Meta:
        db_table = 'doctor_app_testprescriptions'

    def _str_(self):
        return f'Test {self.testname} for Prescription {self.prescription.prescriptionid}'
