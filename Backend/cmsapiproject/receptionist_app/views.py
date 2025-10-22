from rest_framework import viewsets
from .models import Patient, Appointment, Bill_Generation
from .serializers import PatientSerializer, AppointmentSerializer, BillGenerationSerializer
from common.permissions import IsAdminOrReceptionist


class PatientViewSet(viewsets.ModelViewSet):
    queryset = Patient.objects.all()
    serializer_class = PatientSerializer
    permission_classes = [IsAdminOrReceptionist]


class AppointmentViewSet(viewsets.ModelViewSet):
    queryset = Appointment.objects.all()
    serializer_class = AppointmentSerializer
    permission_classes = [IsAdminOrReceptionist]


class BillGenerationViewSet(viewsets.ModelViewSet):
    queryset = Bill_Generation.objects.all()
    serializer_class = BillGenerationSerializer
    permission_classes = [IsAdminOrReceptionist]