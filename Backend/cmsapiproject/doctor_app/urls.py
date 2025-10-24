# doctor_app/urls.py

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    ConsultationViewSet,
    PrescriptionViewSet,
    MedicinePrescriptionViewSet,
    TestPrescriptionViewSet
)

# Create a DRF router
router = DefaultRouter()
router.register(r'consultations', ConsultationViewSet, basename='consultation')
router.register(r'prescriptions', PrescriptionViewSet, basename='prescription')
router.register(r'medicine-prescriptions', MedicinePrescriptionViewSet, basename='medicineprescription')
router.register(r'test-prescriptions', TestPrescriptionViewSet, basename='testprescription')

# URL patterns
urlpatterns = [
    path('', include(router.urls)),
]
