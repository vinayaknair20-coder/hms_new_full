from django.contrib import admin
from .models import Prescription, Consultation, MedicinePrescription, TestPrescription

admin.site.register(Consultation)
admin.site.register(Prescription)   
admin.site.register(MedicinePrescription)
admin.site.register(TestPrescription)