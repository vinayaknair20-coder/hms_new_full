from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ConsultationViewSet, PrescriptionViewSet

router = DefaultRouter()
router.register(r'consultations', ConsultationViewSet)
router.register(r'prescriptions', PrescriptionViewSet)

urlpatterns = [
    path('', include(router.urls)),
]
