from django.contrib import admin
from django.utils.safestring import mark_safe
from .models import Patient, Appointment, Bill_Generation

admin.site.register(Patient)
admin.site.register(Appointment)
admin.site.register(Bill_Generation)