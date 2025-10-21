from rest_framework import serializers
from .models import LabTest, TestOrder, TestResult


class LabTestSerializer(serializers.ModelSerializer):
    class Meta:
        model = LabTest
        fields = '__all__'
    
    def validate_test_name(self, value):
        if not value.strip():
            raise serializers.ValidationError("Test name cannot be empty.")
        if len(value) < 3:
            raise serializers.ValidationError("Test name must be at least 3 characters long.")
        return value
    
    def validate(self, data):
        # Validate range values
        if 'low_range' in data and 'high_range' in data:
            if data['low_range'] >= data['high_range']:
                raise serializers.ValidationError("Low range must be less than high range.")
        
        # Validate price
        if 'price' in data and data['price'] <= 0:
            raise serializers.ValidationError("Price must be greater than zero.")
        
        return data


class TestOrderSerializer(serializers.ModelSerializer):
    test_name = serializers.CharField(source='lab_test.test_name', read_only=True)
    patient_name = serializers.SerializerMethodField()
    test_price = serializers.DecimalField(source='lab_test.price', read_only=True, max_digits=8, decimal_places=2)
    
    class Meta:
        model = TestOrder
        fields = '__all__'
    
    def get_patient_name(self, obj):
        return f"{obj.patient.first_name} {obj.patient.last_name}"
    
    def validate_status(self, value):
        valid_statuses = ['Ordered', 'Sample Collected', 'In Progress', 'Completed', 'Cancelled']
        if value not in valid_statuses:
            raise serializers.ValidationError(f"Status must be one of: {', '.join(valid_statuses)}")
        return value
    
    def validate(self, data):
        # Ensure appointment belongs to the patient
        if 'appointment' in data and 'patient' in data:
            if data['appointment'].patient != data['patient']:
                raise serializers.ValidationError("Appointment does not belong to the specified patient.")
        
        # Check if test is active
        if 'lab_test' in data and not data['lab_test'].is_active:
            raise serializers.ValidationError("Cannot order an inactive test.")
        
        return data


class TestResultSerializer(serializers.ModelSerializer):
    test_name = serializers.CharField(source='test_order.lab_test.test_name', read_only=True)
    patient_name = serializers.SerializerMethodField()
    normal_range = serializers.SerializerMethodField()
    unit = serializers.CharField(source='test_order.lab_test.unit', read_only=True)
    
    class Meta:
        model = TestResult
        fields = '__all__'
        read_only_fields = ('is_normal', 'result_date')
    
    def get_patient_name(self, obj):
        return f"{obj.test_order.patient.first_name} {obj.test_order.patient.last_name}"
    
    def get_normal_range(self, obj):
        test = obj.test_order.lab_test
        return f"{test.low_range} - {test.high_range} {test.unit}"
    
    def validate_result_value(self, value):
        if value < 0:
            raise serializers.ValidationError("Result value cannot be negative.")
        return value
    
    def validate(self, data):
        # Ensure test order exists and is in appropriate status
        if 'test_order' in data:
            if data['test_order'].status == 'Cancelled':
                raise serializers.ValidationError("Cannot add results for a cancelled test order.")
            if data['test_order'].status == 'Ordered':
                raise serializers.ValidationError("Sample must be collected before entering results.")
        
        return data
