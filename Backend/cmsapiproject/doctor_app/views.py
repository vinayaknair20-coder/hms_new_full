"""
Doctor App Views
Consultation and Prescription Management
"""

from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404
from django.utils import timezone
from django.db.models import Count, Q
from datetime import datetime, timedelta

from .models import (
    Consultation,
    Prescription,
    MedicinePrescription,
    TestPrescription
)
from .serializers import (
    ConsultationSerializer,
    PrescriptionSerializer,
    MedicinePrescriptionSerializer,
    TestPrescriptionSerializer,
    PrescriptionCreateSerializer
)
from .permissions import IsDoctor  # Local permissions
from receptionist_app.models import Appointment
from admin_app.models import Staff




class ConsultationViewSet(viewsets.ModelViewSet):
    """Consultation Management ViewSet"""
    
    # Corrected select_related: follow foreign keys properly
    queryset = Consultation.objects.select_related(
        'appointment__patient',  # appointment → patient
        'doctor__user'           # doctor → user
    ).all()
    
    serializer_class = ConsultationSerializer
    # permission_classes = [IsAuthenticated, IsDoctor]  # Enable in production

    def get_queryset(self):
        """Filter consultations by doctor if the user is a doctor"""
        queryset = super().get_queryset()
        if hasattr(self.request.user, 'role') and self.request.user.role == 'Doctor':
            queryset = queryset.filter(doctor__user=self.request.user)
        return queryset

    @action(detail=False, methods=['get'])
    def today(self, request):
        """Get today's consultations"""
        today = timezone.now().date()
        consultations = self.get_queryset().filter(consultationdate=today).order_by('-consultationtime')
        serializer = self.get_serializer(consultations, many=True)
        return Response({
            'date': today,
            'count': consultations.count(),
            'consultations': serializer.data
        }, status=status.HTTP_200_OK)

    @action(detail=False, methods=['get'])
    def upcoming(self, request):
        """Get upcoming consultations"""
        today = timezone.now().date()
        consultations = self.get_queryset().filter(
            consultationdate__gte=today,
            status__in=['SCHEDULED', 'INPROGRESS']
        ).order_by('consultationdate', 'consultationtime')
        serializer = self.get_serializer(consultations, many=True)
        return Response({
            'count': consultations.count(),
            'consultations': serializer.data
        }, status=status.HTTP_200_OK)

    @action(detail=False, methods=['get'])
    def statistics(self, request):
        """Get consultation statistics"""
        queryset = self.get_queryset()
        today = timezone.now().date()
        stats = {
            'total': queryset.count(),
            'today': queryset.filter(consultationdate=today).count(),
            'completed': queryset.filter(status='COMPLETED').count(),
            'pending': queryset.filter(status__in=['SCHEDULED', 'INPROGRESS']).count(),
            'cancelled': queryset.filter(status='CANCELLED').count()
        }
        return Response(stats, status=status.HTTP_200_OK)

    @action(detail=True, methods=['post'])
    def complete(self, request, pk=None):
        """Mark consultation as completed"""
        consultation = self.get_object()
        consultation.status = 'COMPLETED'
        consultation.save()
        return Response({
            'message': 'Consultation marked as completed',
            'consultation_id': consultation.consultationid,
            'status': consultation.status
        }, status=status.HTTP_200_OK)

    @action(detail=True, methods=['post'])
    def cancel(self, request, pk=None):
        """Cancel consultation"""
        consultation = self.get_object()
        consultation.status = 'CANCELLED'
        consultation.save()
        return Response({
            'message': 'Consultation cancelled',
            'consultation_id': consultation.consultationid,
            'status': consultation.status
        }, status=status.HTTP_200_OK)


class PrescriptionViewSet(viewsets.ModelViewSet):
    queryset = Prescription.objects.all()
    serializer_class = PrescriptionSerializer  # Default for GET

    def get_serializer_class(self):
        if self.action in ['create', 'update', 'partial_update']:
            return PrescriptionCreateSerializer
        return PrescriptionSerializer


class MedicinePrescriptionViewSet(viewsets.ModelViewSet):
    """Medicine Prescription ViewSet"""
    queryset = MedicinePrescription.objects.select_related(
        'prescription'
    )
    serializer_class = MedicinePrescriptionSerializer
    # permission_classes = [IsAuthenticated]  # Enable in production


class TestPrescriptionViewSet(viewsets.ModelViewSet):
    """Test Prescription ViewSet"""
    queryset = TestPrescription.objects.select_related(
        'prescription'
    )
    serializer_class = TestPrescriptionSerializer
    # permission_classes = [IsAuthenticated]  # Enable in production


from pharmacist_app.models import Medicine
from rest_framework.viewsets import ReadOnlyModelViewSet


class PharmacyMedicineProxyViewSet(ReadOnlyModelViewSet):
    """Proxy view for doctors to search/view available medicines"""
    queryset = Medicine.objects.all()
    permission_classes = [IsAuthenticated, IsDoctor]

    def get_queryset(self):
        queryset = super().get_queryset()
        search = self.request.query_params.get('search', '')
        if search:
            queryset = queryset.filter(name__icontains=search)
        return queryset

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        data = [{
            'id': med.id,
            'name': med.name,
            'description': med.description,
            'in_stock': med.stock > 0
        } for med in queryset]
        return Response(data)
