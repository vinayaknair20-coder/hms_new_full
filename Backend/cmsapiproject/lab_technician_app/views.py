from rest_framework import viewsets, filters, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.utils import timezone
from .models import LabTest, TestOrder, TestResult
from .serializers import LabTestSerializer, TestOrderSerializer, TestResultSerializer
from common.permissions import IsAdmin, IsAdminOrReceptionist


class LabTestViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing Lab Test catalog
    Admins and Receptionists can manage tests
    """
    queryset = LabTest.objects.all()
    serializer_class = LabTestSerializer
    permission_classes = [IsAdminOrReceptionist]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['test_name', 'description']
    ordering_fields = ['test_name', 'price', 'created_at']
    
    @action(detail=False, methods=['get'])
    def active_tests(self, request):
        """Get only active tests"""
        active = LabTest.objects.filter(is_active=True)
        serializer = self.get_serializer(active, many=True)
        return Response(serializer.data)


class TestOrderViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing Test Orders
    """
    queryset = TestOrder.objects.all()
    serializer_class = TestOrderSerializer
    permission_classes = [IsAdminOrReceptionist]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['patient__first_name', 'patient__last_name', 'lab_test__test_name']
    ordering_fields = ['ordered_date', 'status', 'priority']
    
    @action(detail=True, methods=['post'])
    def collect_sample(self, request, pk=None):
        """Mark sample as collected"""
        test_order = self.get_object()
        if test_order.status != 'Ordered':
            return Response(
                {'error': 'Sample can only be collected for orders with status "Ordered"'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        test_order.status = 'Sample Collected'
        test_order.sample_collection_date = timezone.now()
        test_order.save()
        
        serializer = self.get_serializer(test_order)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def pending_tests(self, request):
        """Get tests that need processing"""
        pending = TestOrder.objects.exclude(status__in=['Completed', 'Cancelled'])
        serializer = self.get_serializer(pending, many=True)
        return Response(serializer.data)


class TestResultViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing Test Results
    """
    queryset = TestResult.objects.all()
    serializer_class = TestResultSerializer
    permission_classes = [IsAdminOrReceptionist]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['test_order__patient__first_name', 'test_order__patient__last_name']
    ordering_fields = ['result_date', 'is_normal']
    
    @action(detail=True, methods=['post'])
    def verify_result(self, request, pk=None):
        """Verify test result by senior staff"""
        test_result = self.get_object()
        
        if test_result.verified_by:
            return Response(
                {'error': 'Result already verified'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        verifier_id = request.data.get('verified_by')
        if not verifier_id:
            return Response(
                {'error': 'verified_by field is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        test_result.verified_by_id = verifier_id
        test_result.verified_date = timezone.now()
        test_result.save()
        
        serializer = self.get_serializer(test_result)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def abnormal_results(self, request):
        """Get results outside normal range"""
        abnormal = TestResult.objects.filter(is_normal=False)
        serializer = self.get_serializer(abnormal, many=True)
        return Response(serializer.data)
