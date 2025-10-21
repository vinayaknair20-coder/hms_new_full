from django.contrib import admin
from .models import Medicine, PrescriptionMedicine, MedicineStockHistory, MedicineBilling

admin.site.register(Medicine)
admin.site.register(PrescriptionMedicine)
admin.site.register(MedicineStockHistory)
admin.site.register(MedicineBilling)
