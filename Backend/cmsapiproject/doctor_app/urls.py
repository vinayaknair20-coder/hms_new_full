from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    ConsultationViewSet, PrescriptionViewSet, PharmacyMedicineProxyViewSet
)

router = DefaultRouter()
router.register(r'consultations', ConsultationViewSet, basename='consultation')
router.register(r'prescriptions', PrescriptionViewSet, basename='prescription')

urlpatterns = [
    path('', include(router.urls)),
    # Add a direct path for medicine list
    # (medicine search/lookup is provided by pharmacist_app endpoints)
    path('pharmacy-medicines/', PharmacyMedicineProxyViewSet.as_view({'get': 'list'}), name='pharmacy-medicines-list'),
]