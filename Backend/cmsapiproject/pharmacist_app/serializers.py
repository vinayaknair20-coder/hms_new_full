from rest_framework import serializers
from .models import Medicine, PrescriptionMedicine, MedicineStockHistory, MedicineBilling

class MedicineSerializer(serializers.ModelSerializer):
    class Meta:
        model = Medicine
        fields = '__all__'

    def validate_stock(self, value):
        if value < 0:
            raise serializers.ValidationError("Stock cannot be negative.")
        return value

    def validate_price_per_unit(self, value):
        if value <= 0:
            raise serializers.ValidationError("Price per unit must be positive.")
        return value

class PrescriptionMedicineSerializer(serializers.ModelSerializer):
    class Meta:
        model = PrescriptionMedicine
        fields = '__all__'

    def validate_quantity(self, value):
        if value <= 0:
            raise serializers.ValidationError("Quantity must be greater than zero.")
        return value

class MedicineStockHistorySerializer(serializers.ModelSerializer):
    class Meta:
        model = MedicineStockHistory
        fields = '__all__'

    def validate_change(self, value):
        if value == 0:
            raise serializers.ValidationError("Stock change cannot be zero.")
        return value

class MedicineBillingSerializer(serializers.ModelSerializer):
    class Meta:
        model = MedicineBilling
        fields = '__all__'
        read_only_fields = ('total_medicine_fee',)

    def validate_total_medicine_fee(self, value):
        if value < 0:
            raise serializers.ValidationError("Total medicine fee cannot be negative.")
        return value
