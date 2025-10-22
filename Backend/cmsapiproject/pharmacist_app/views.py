from django.shortcuts import render
from rest_framework import viewsets, filters, status
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.db.models import Q
from django.db import transaction

# Import models
from .models import Medicine, PrescriptionMedicine, MedicineStockHistory, MedicineBilling, QuickSale, QuickSaleItem

# Import serializers
from .serializers import (
    MedicineSerializer, 
    PrescriptionMedicineSerializer, 
    MedicineStockHistorySerializer, 
    MedicineBillingSerializer
)

# Import common permissions
from common.permissions import IsDoctor, IsAdmin, IsReceptionist, IsAdminOrPharmacist


# ========================
# PHARMACIST PROFILE VIEW
# ========================
@api_view(['GET'])
@permission_classes([IsAuthenticated])  # Changed from IsPharmacist to IsAuthenticated
def get_pharmacist_profile(request):
    """Get pharmacist profile information"""
    user = request.user
    
    # Check if user is pharmacist
    if user.role != 'Pharmacist':
        return Response({'error': 'Access denied. Pharmacist role required.'}, status=403)
    
    try:
        staff = user.staff
        return Response({
            'id': user.id,
            'username': user.username,
            'role': user.role,
            'first_name': user.first_name,
            'last_name': user.last_name,
            'email': user.email,
            'staff_id': staff.id,
            'phone': staff.phone,
            'blood_group': staff.blood_group,
            'address': staff.address
        })
    except Exception as e:
        return Response({'error': 'Staff profile not found'}, status=404)


# ========================
# MEDICINE VIEWSET
# ========================
class MedicineViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing Medicine catalog
    Handles CRUD operations + custom actions for pharmacist workflows
    """
    queryset = Medicine.objects.all()
    serializer_class = MedicineSerializer
    permission_classes = [IsAdmin | IsAdminOrPharmacist]
    
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name', 'description']
    ordering_fields = ['name', 'stock', 'price_per_unit']
    ordering = ['name']
    
    @action(detail=False, methods=['get'], url_path='low-stock')
    def low_stock(self, request):
        """
        Get medicines with stock below threshold (20 units)
        Endpoint: GET /medicines/low-stock/
        """
        threshold = 20
        low_stock_medicines = Medicine.objects.filter(stock__lt=threshold).order_by('stock')
        serializer = self.get_serializer(low_stock_medicines, many=True)
        return Response({
            'count': low_stock_medicines.count(),
            'threshold': threshold,
            'medicines': serializer.data
        })

    @action(detail=False, methods=['post'], url_path='quick-sale')
    def quick_sale(self, request):
        """
        Process a quick sale without prescription
        Endpoint: POST /medicines/quick-sale/
        """
        customer_name = request.data.get('customer_name')
        customer_phone = request.data.get('customer_phone', '')
        items = request.data.get('items', [])
        
        if not customer_name:
            return Response({'error': 'Customer name is required'}, status=status.HTTP_400_BAD_REQUEST)
        
        if not items:
            return Response({'error': 'No items in cart'}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            with transaction.atomic():
                quick_sale = QuickSale.objects.create(
                    customer_name=customer_name,
                    customer_phone=customer_phone,
                    total_amount=0,
                    created_by=request.user.staff if hasattr(request.user, 'staff') else None
                )
                
                total = 0
                sale_items = []
                
                for item in items:
                    medicine = Medicine.objects.get(id=item['medicine_id'])
                    price = medicine.price_per_unit
                    item_total = price * item['quantity']
                    total += item_total
                    
                    QuickSaleItem.objects.create(
                        quick_sale=quick_sale,
                        medicine=medicine,
                        quantity=item['quantity'],
                        price=price
                    )
                    
                    sale_items.append({
                        'medicine': medicine.name,
                        'quantity': item['quantity'],
                        'price': float(price),
                        'total': float(item_total)
                    })
                
                quick_sale.total_amount = total
                quick_sale.save()
                
                return Response({
                    'sale_id': f'QS-{quick_sale.id}',
                    'customer_name': customer_name,
                    'customer_phone': customer_phone,
                    'date': quick_sale.timestamp.date().isoformat(),
                    'items': sale_items,
                    'total_amount': float(total)
                }, status=status.HTTP_201_CREATED)
        
        except Medicine.DoesNotExist:
            return Response({'error': 'Medicine not found'}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)


# ========================
# PRESCRIPTION MEDICINE VIEWSET
# ========================
class PrescriptionMedicineViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing Prescription-Medicine relationships
    """
    queryset = PrescriptionMedicine.objects.all()
    serializer_class = PrescriptionMedicineSerializer
    permission_classes = [IsAdmin | IsAdminOrPharmacist]
    
    filter_backends = [filters.OrderingFilter]
    ordering_fields = ['prescription', 'medicine', 'quantity']


# ========================
# STOCK HISTORY VIEWSET
# ========================
class MedicineStockHistoryViewSet(viewsets.ModelViewSet):
    """
    ViewSet for tracking medicine stock changes
    """
    queryset = MedicineStockHistory.objects.all()
    serializer_class = MedicineStockHistorySerializer
    permission_classes = [IsAdmin | IsAdminOrPharmacist]
    
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['reason', 'medicine__name']
    ordering_fields = ['timestamp', 'medicine', 'change']
    ordering = ['-timestamp']


# ========================
# BILLING VIEWSET
# ========================
class MedicineBillingViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing medicine billing
    """
    queryset = MedicineBilling.objects.all()
    serializer_class = MedicineBillingSerializer
    permission_classes = [IsAdmin | IsAdminOrPharmacist]
    
    filter_backends = [filters.OrderingFilter]
    ordering_fields = ['timestamp', 'total_medicine_fee', 'patient']
    ordering = ['-timestamp']
    
    @action(detail=False, methods=['get'], url_path='pending-prescriptions')
    def pending_prescriptions(self, request):
        """
        Get all prescriptions that haven't been billed yet
        Endpoint: GET /medicinebilling/pending-prescriptions/
        """
        from doctor_app.models import Prescription
        
        billed_prescription_ids = MedicineBilling.objects.values_list('prescription_id', flat=True)
        
        pending_prescriptions = Prescription.objects.exclude(
            id__in=billed_prescription_ids
        ).select_related('doctor', 'consultation__patient')
        
        pending_data = []
        for prescription in pending_prescriptions:
            try:
                patient = prescription.consultation.patient
                patient_name = patient.Patient_name
                
                doctor = prescription.doctor
                doctor_name = doctor.user.username
                
                pending_data.append({
                    'prescription_id': prescription.id,
                    'patient_name': patient_name,
                    'doctor_name': doctor_name,
                    'prescription_date': prescription.date_time,
                    'dosage': prescription.dosage,
                    'frequency': prescription.frequency,
                    'duration': prescription.duration,
                })
            except AttributeError:
                continue
        
        return Response({
            'count': len(pending_data),
            'pending_prescriptions': pending_data
        })
    
    @action(detail=False, methods=['get'], url_path='billing-summary')
    def billing_summary(self, request):
        """
        Get summary of billing statistics
        Endpoint: GET /medicinebilling/billing-summary/
        """
        from django.db.models import Sum, Avg, Count
        
        summary = MedicineBilling.objects.aggregate(
            total_bills=Count('id'),
            total_revenue=Sum('total_medicine_fee'),
            average_bill=Avg('total_medicine_fee')
        )
        
        return Response(summary)
