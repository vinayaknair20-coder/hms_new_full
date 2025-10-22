from django.shortcuts import render
from rest_framework import viewsets, filters, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db.models import Q
from django.db import transaction


from .models import Medicine, PrescriptionMedicine, MedicineStockHistory, MedicineBilling, QuickSale, QuickSaleItem
from .serializers import (
    MedicineSerializer, 
    PrescriptionMedicineSerializer, 
    MedicineStockHistorySerializer, 
    MedicineBillingSerializer
)
from common.permissions import IsDoctor, IsPharmacist, IsAdmin, IsReceptionist, IsAdminOrPharmacist



class MedicineViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing Medicine catalog
    Handles CRUD operations + custom actions for pharmacist workflows
    """
    queryset = Medicine.objects.all()
    serializer_class = MedicineSerializer
    permission_classes = [IsAdmin | IsPharmacist]
    
    # ==== NEW: Add search and filter functionality ====
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name', 'description']  # Search medicines by name or description
    ordering_fields = ['name', 'stock', 'price_per_unit']  # Allow ordering by these fields
    ordering = ['name']  # Default ordering
    
    # ==== NEW: Custom action for low stock medicines ====
    @action(detail=False, methods=['get'], url_path='low-stock')
    def low_stock(self, request):
        """
        Get medicines with stock below threshold (20 units)
        Endpoint: GET /medicines/low-stock/
        Returns: List of medicines with stock < 20
        """
        threshold = 20  # Low stock threshold set to 20 units
        low_stock_medicines = Medicine.objects.filter(stock__lt=threshold).order_by('stock')
        serializer = self.get_serializer(low_stock_medicines, many=True)
        return Response({
            'count': low_stock_medicines.count(),
            'threshold': threshold,
            'medicines': serializer.data
        })

    # ========== NEW: QUICK SALE ENDPOINT ==========
    @action(detail=False, methods=['post'], url_path='quick-sale')
    def quick_sale(self, request):
        """
        Process a quick sale without prescription
        Endpoint: POST /medicines/quick-sale/
        Body: {
            "customer_name": "John Doe",
            "customer_phone": "1234567890",
            "items": [{"medicine_id": 1, "quantity": 2}]
        }
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
                # Create QuickSale record
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
                    
                    # Create QuickSaleItem (automatically updates stock)
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
                
                # Update total
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



class PrescriptionMedicineViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing Prescription-Medicine relationships
    Links prescriptions to specific medicines with quantities
    """
    queryset = PrescriptionMedicine.objects.all()
    serializer_class = PrescriptionMedicineSerializer
    permission_classes = [IsAdmin | IsPharmacist]
    
    # ==== NEW: Add filtering capability ====
    filter_backends = [filters.OrderingFilter]
    ordering_fields = ['prescription', 'medicine', 'quantity']



class MedicineStockHistoryViewSet(viewsets.ModelViewSet):
    """
    ViewSet for tracking medicine stock changes
    Maintains audit trail of all stock movements
    """
    queryset = MedicineStockHistory.objects.all()
    serializer_class = MedicineStockHistorySerializer
    permission_classes = [IsAdmin | IsPharmacist]
    
    # ==== NEW: Add search and ordering ====
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['reason', 'medicine__name']  # Search by reason or medicine name
    ordering_fields = ['timestamp', 'medicine', 'change']
    ordering = ['-timestamp']  # Latest first by default



class MedicineBillingViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing medicine billing
    Handles billing operations + custom actions for pharmacist workflows
    """
    queryset = MedicineBilling.objects.all()
    serializer_class = MedicineBillingSerializer
    permission_classes = [IsAdmin | IsPharmacist]
    
    # ==== NEW: Add ordering capability ====
    filter_backends = [filters.OrderingFilter]
    ordering_fields = ['timestamp', 'total_medicine_fee', 'patient']
    ordering = ['-timestamp']  # Latest bills first
    
    # ==== NEW: Custom action to view pending prescriptions ====
    @action(detail=False, methods=['get'], url_path='pending-prescriptions')
    def pending_prescriptions(self, request):
        """
        Get all prescriptions that haven't been billed yet
        Endpoint: GET /medicinebilling/pending-prescriptions/
        Returns: List of prescription IDs that need to be dispensed
        """
        from doctor_app.models import Prescription
        
        # Get all prescription IDs that have been billed
        billed_prescription_ids = MedicineBilling.objects.values_list('prescription_id', flat=True)
        
        # Get prescriptions that haven't been billed yet
        pending_prescriptions = Prescription.objects.exclude(
            id__in=billed_prescription_ids
        ).select_related('doctor', 'consultation__patient')
        
        # Format response with prescription details
        pending_data = []
        for prescription in pending_prescriptions:
            pending_data.append({
                'prescription_id': prescription.id,
                'patient_name': f"{prescription.consultation.patient.first_name} {prescription.consultation.patient.last_name}",
                'doctor_name': f"{prescription.doctor.user.first_name} {prescription.doctor.user.last_name}",
                'prescription_date': prescription.date_time,
                'dosage': prescription.dosage,
                'frequency': prescription.frequency,
                'duration': prescription.duration,
            })
        
        return Response({
            'count': len(pending_data),
            'pending_prescriptions': pending_data
        })
    
    # ==== NEW: Custom action to get billing summary ====
    @action(detail=False, methods=['get'], url_path='billing-summary')
    def billing_summary(self, request):
        """
        Get summary of billing statistics
        Endpoint: GET /medicinebilling/billing-summary/
        Returns: Total bills, total revenue, average bill amount
        """
        from django.db.models import Sum, Avg, Count
        
        summary = MedicineBilling.objects.aggregate(
            total_bills=Count('id'),
            total_revenue=Sum('total_medicine_fee'),
            average_bill=Avg('total_medicine_fee')
        )
        
        return Response(summary)
