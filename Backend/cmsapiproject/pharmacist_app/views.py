from rest_framework import viewsets
from .models import Medicine, PrescriptionMedicine, MedicineStockHistory, MedicineBilling
from .serializers import MedicineSerializer, PrescriptionMedicineSerializer, MedicineStockHistorySerializer, MedicineBillingSerializer
from common.permissions import IsDoctor, IsPharmacist, IsAdmin, IsReceptionist, IsAdminOrPharmacist

class MedicineViewSet(viewsets.ModelViewSet):
    queryset = Medicine.objects.all()
    serializer_class = MedicineSerializer
    permission_classes = [IsAdmin | IsPharmacist]

class PrescriptionMedicineViewSet(viewsets.ModelViewSet):
    queryset = PrescriptionMedicine.objects.all()
    serializer_class = PrescriptionMedicineSerializer
    permission_classes = [IsAdmin | IsPharmacist]

class MedicineStockHistoryViewSet(viewsets.ModelViewSet):
    queryset = MedicineStockHistory.objects.all()
    serializer_class = MedicineStockHistorySerializer
    permission_classes = [IsAdmin | IsPharmacist]

class MedicineBillingViewSet(viewsets.ModelViewSet):
    queryset = MedicineBilling.objects.all()
    serializer_class = MedicineBillingSerializer
    permission_classes = [IsAdminOrPharmacist]