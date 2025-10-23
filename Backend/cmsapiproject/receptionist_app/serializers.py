from rest_framework import serializers
from .models import Patient, Appointment, Bill_Generation
from django.utils import timezone


class PatientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Patient
        fields = '__all__'

    # Phone number validation
    def validate_phone(self, value):
        if not value.isdigit():
            raise serializers.ValidationError("Phone number must contain only digits.")
        if len(value) != 10:
            raise serializers.ValidationError("Phone number must be exactly 10 digits.")
        return value
    # Patient name validation
    def validate_Patient_name(self, value):
        if len(value.strip()) < 3:
            raise serializers.ValidationError("Patient name must be at least 3 letters long.")
            # Check if original value starts with space
        if value[0].isspace():
            raise serializers.ValidationError("Patient name cannot start with a space.")
        
        return value

    # Date of birth validation
    def validate_dob(self, value):
        if value and value > timezone.now().date():
            raise serializers.ValidationError("Date of birth cannot be in the future.")
        return value


class AppointmentSerializer(serializers.ModelSerializer):
    # Show doctor's name and patient's name in response
    doctor_name = serializers.CharField(source='doctor_id.staff_name', read_only=True)
    patient_name = serializers.CharField(source='Patient_id.Patient_name', read_only=True)

    class Meta:
        model = Appointment
        fields = '__all__'

    def validate_Appointment_date(self, value):
        # Appointment date must not be in the past
        if value < timezone.now().date():
            raise serializers.ValidationError("Appointment date cannot be in the past.")
        return value


class BillGenerationSerializer(serializers.ModelSerializer):
    # Readable names for reference
    patient_name = serializers.CharField(source='Patient_id.Patient_name', read_only=True)
    appointment_date = serializers.DateField(source='Appointment_id.Appointment_date', read_only=True)
    doctor_name = serializers.CharField(source='Appointment_id.doctor_id.staff_name', read_only=True)

    class Meta:
        model = Bill_Generation
        fields = '__all__'
        read_only_fields = ('Billing_date', 'Token')

    def validate_Amount(self, value):
        if value <= 0:
            raise serializers.ValidationError("Amount must be a positive number.")
        return value
