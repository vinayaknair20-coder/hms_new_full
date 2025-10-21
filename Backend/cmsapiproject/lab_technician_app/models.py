from django.db import models
from admin_app.models import Staff
from receptionist_app.models import Patient, Appointment


class LabTest(models.Model):
    """
    Lab Test catalog - defines available tests with their parameters
    """
    test_name = models.CharField(max_length=200)
    low_range = models.DecimalField(max_digits=10, decimal_places=2, help_text="Normal range lower limit")
    high_range = models.DecimalField(max_digits=10, decimal_places=2, help_text="Normal range upper limit")
    unit = models.CharField(max_length=50, help_text="e.g., mg/dL, %, count/mm3")
    price = models.DecimalField(max_digits=8, decimal_places=2)
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.test_name} ({self.unit})"
    
    class Meta:
        ordering = ['test_name']


class TestOrder(models.Model):
    """
    Test ordered for a patient - links appointment to specific tests
    """
    STATUS_CHOICES = [
        ('Ordered', 'Ordered'),
        ('Sample Collected', 'Sample Collected'),
        ('In Progress', 'In Progress'),
        ('Completed', 'Completed'),
        ('Cancelled', 'Cancelled'),
    ]
    
    PRIORITY_CHOICES = [
        ('Normal', 'Normal'),
        ('Urgent', 'Urgent'),
        ('STAT', 'STAT')
    ]
    
    appointment = models.ForeignKey(Appointment, on_delete=models.CASCADE, related_name='test_orders')
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE)
    lab_test = models.ForeignKey(LabTest, on_delete=models.CASCADE)
    ordered_by = models.ForeignKey(Staff, on_delete=models.SET_NULL, null=True, related_name='ordered_tests', 
                                     help_text="Doctor/Staff who ordered the test")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Ordered')
    priority = models.CharField(max_length=20, choices=PRIORITY_CHOICES, default='Normal')
    ordered_date = models.DateTimeField(auto_now_add=True)
    sample_collection_date = models.DateTimeField(null=True, blank=True)
    
    def __str__(self):
        return f"{self.lab_test.test_name} for {self.patient.first_name} {self.patient.last_name}"


class TestResult(models.Model):
    """
    Actual test results entered by lab technician
    """
    test_order = models.OneToOneField(TestOrder, on_delete=models.CASCADE, related_name='result')
    result_value = models.DecimalField(max_digits=10, decimal_places=2)
    is_normal = models.BooleanField(default=True, help_text="Is result within normal range?")
    technician_notes = models.TextField(blank=True)
    performed_by = models.ForeignKey(Staff, on_delete=models.SET_NULL, null=True, 
                                      related_name='performed_tests',
                                      help_text="Lab technician who performed the test")
    verified_by = models.ForeignKey(Staff, on_delete=models.SET_NULL, null=True, blank=True,
                                     related_name='verified_tests',
                                     help_text="Senior technician/doctor who verified results")
    result_date = models.DateTimeField(auto_now_add=True)
    verified_date = models.DateTimeField(null=True, blank=True)
    
    def save(self, *args, **kwargs):
        # Auto-determine if result is within normal range
        test = self.test_order.lab_test
        if test.low_range <= self.result_value <= test.high_range:
            self.is_normal = True
        else:
            self.is_normal = False
        
        # Update test order status to Completed
        self.test_order.status = 'Completed'
        self.test_order.save()
        
        super().save(*args, **kwargs)
    
    def __str__(self):
        return f"{self.test_order.lab_test.test_name}: {self.result_value} {self.test_order.lab_test.unit}"
