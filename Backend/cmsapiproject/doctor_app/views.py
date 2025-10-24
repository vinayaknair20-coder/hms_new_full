from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.utils import timezone

from .models import Consultation, Prescription, MedicinePrescription, TestPrescription
from .serializers import (
    ConsultationSerializer,
    PrescriptionSerializer,
    PrescriptionCreateSerializer,
    MedicinePrescriptionSerializer,
    TestPrescriptionSerializer
)


class ConsultationViewSet(viewsets.ModelViewSet):
    queryset = Consultation.objects.select_related(
        'appointment__Patient',  # Match exact field name
        'doctor__user'
    ).all()
    serializer_class = ConsultationSerializer

    def get_queryset(self):
        queryset = super().get_queryset()
        user = self.request.user
        if hasattr(user, 'role') and user.role == 'Doctor':
            queryset = queryset.filter(doctor__user=user)
        return queryset

    @action(detail=False, methods=['get'])
    def today(self, request):
        today = timezone.now().date()
        consultations = self.get_queryset().filter(consultationdate=today).order_by('-consultationtime')
        serializer = self.get_serializer(consultations, many=True)
        return Response({'date': today, 'count': consultations.count(), 'consultations': serializer.data})

    @action(detail=False, methods=['get'])
    def upcoming(self, request):
        today = timezone.now().date()
        consultations = self.get_queryset().filter(
            consultationdate__gte=today,
            status__in=['SCHEDULED', 'INPROGRESS']
        ).order_by('consultationdate', 'consultationtime')
        serializer = self.get_serializer(consultations, many=True)
        return Response({'count': consultations.count(), 'consultations': serializer.data})

    @action(detail=True, methods=['get', 'post'])
    def prescription(self, request, pk=None):
        consultation = self.get_object()
        prescription = getattr(consultation, 'prescriptions', None)
        if request.method == 'GET':
            if prescription:
                serializer = PrescriptionSerializer(prescription)
                return Response(serializer.data)
            return Response({'message': 'No prescription found'}, status=status.HTTP_404_NOT_FOUND)
        else:
            if prescription:
                serializer = PrescriptionCreateSerializer(prescription, data=request.data)
            else:
                serializer = PrescriptionCreateSerializer(data={**request.data, 'consultation': consultation.consultationid})
            serializer.is_valid(raise_exception=True)
            serializer.save(consultation=consultation)
            return Response(serializer.data)

class PrescriptionViewSet(viewsets.ModelViewSet):
    queryset = Prescription.objects.all()
    serializer_class = PrescriptionSerializer

    def get_serializer_class(self):
        if self.action in ['create', 'update', 'partial_update']:
            return PrescriptionCreateSerializer
        return PrescriptionSerializer

class MedicinePrescriptionViewSet(viewsets.ModelViewSet):
    queryset = MedicinePrescription.objects.select_related('prescription')
    serializer_class = MedicinePrescriptionSerializer

class TestPrescriptionViewSet(viewsets.ModelViewSet):
    queryset = TestPrescription.objects.select_related('prescription')
    serializer_class = TestPrescriptionSerializer
