from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    MedicineViewSet, 
    PrescriptionMedicineViewSet, 
    MedicineStockHistoryViewSet, 
    MedicineBillingViewSet,
    get_pharmacist_profile
)

router = DefaultRouter()
router.register(r'medicines', MedicineViewSet)
router.register(r'prescriptionmedicines', PrescriptionMedicineViewSet)
router.register(r'medicinestockhistory', MedicineStockHistoryViewSet)
router.register(r'medicinebilling', MedicineBillingViewSet)

urlpatterns = [
    path('me/', get_pharmacist_profile, name='pharmacist-profile'),
    path('', include(router.urls)),
]
