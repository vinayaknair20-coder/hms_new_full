from django.db import models
from doctor_app.models import Prescription
from receptionist_app.models import Patient ,Appointment
from admin_app.models import Staff


class Medicine(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    stock = models.PositiveIntegerField(default=0)
    price_per_unit = models.DecimalField(max_digits=8, decimal_places=2)

    def __str__(self):
        return self.name

class PrescriptionMedicine(models.Model):
    prescription = models.ForeignKey(Prescription, on_delete=models.CASCADE)
    medicine = models.ForeignKey(Medicine, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()

class MedicineStockHistory(models.Model):
    medicine = models.ForeignKey(Medicine, on_delete=models.CASCADE)
    change = models.IntegerField(help_text="Add positive for received, negative for dispensed")
    reason = models.CharField(max_length=255, help_text="Delivered, Correction, Dispensed, etc.")
    related_prescription = models.ForeignKey(Prescription, on_delete=models.SET_NULL, null=True, blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)

class MedicineBilling(models.Model):
    prescription = models.ForeignKey(Prescription, on_delete=models.CASCADE)
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE)
    # medicines field removed: billing is derived from PrescriptionMedicine lines
    total_medicine_fee = models.DecimalField(max_digits=10, decimal_places=2)
    created_by = models.ForeignKey(Staff, on_delete=models.SET_NULL, null=True)  # Pharmacist
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Medicine Billing for Prescription #{self.prescription.id}"

    def compute_total(self):
        # compute total from prescription lines
        lines = PrescriptionMedicine.objects.filter(prescription=self.prescription)
        total = 0
        for line in lines:
            total += line.medicine.price_per_unit * line.quantity
        return total

    def save(self, *args, **kwargs):
        # On create: compute total and decrement stock atomically
        from django.db import transaction
        from django.core.exceptions import ValidationError

        is_new = self._state.adding
        if is_new:
            # compute total
            total = self.compute_total()
            self.total_medicine_fee = total
            # perform stock decrement and create stock history inside a transaction
            with transaction.atomic():
                super().save(*args, **kwargs)
                lines = PrescriptionMedicine.objects.select_related('medicine').filter(prescription=self.prescription)
                for line in lines:
                    med = line.medicine
                    if med.stock < line.quantity:
                        raise ValidationError(f"Insufficient stock for {med.name}")
                    med.stock = med.stock - line.quantity
                    med.save()
                    MedicineStockHistory.objects.create(
                        medicine=med,
                        change=-line.quantity,
                        reason='Dispensed by billing',
                        related_prescription=self.prescription
                    )
        else:
            super().save(*args, **kwargs)

