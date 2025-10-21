from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import LabTestViewSet, TestOrderViewSet, TestResultViewSet

router = DefaultRouter()
router.register(r'lab-tests', LabTestViewSet, basename='labtest')
router.register(r'test-orders', TestOrderViewSet, basename='testorder')
router.register(r'test-results', TestResultViewSet, basename='testresult')

urlpatterns = [
    path('', include(router.urls)),
]
