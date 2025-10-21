from django.shortcuts import render
from rest_framework import viewsets
from .models import Consultation, Prescription
from .serializers import ConsultationSerializer, PrescriptionSerializer
from common.permissions import IsDoctor, IsPharmacist, IsAdmin, IsReceptionist, IsAdminOrDoctor


class ConsultationViewSet(viewsets.ModelViewSet):
    queryset = Consultation.objects.all()
    serializer_class = ConsultationSerializer
    permission_classes = [IsAdminOrDoctor]

class PrescriptionViewSet(viewsets.ModelViewSet):
    queryset = Prescription.objects.all()
    serializer_class = PrescriptionSerializer
    permission_classes = [IsAdminOrDoctor]
