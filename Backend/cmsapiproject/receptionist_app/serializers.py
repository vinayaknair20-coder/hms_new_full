from rest_framework import serializers
from .models import Patient, Appointment, Billing
from django.utils import timezone

class PatientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Patient
        fields = '__all__'

    def validate_phone(self, value):
        if len(value) < 10:
            raise serializers.ValidationError("Phone number must be at least 10 digits.")
        return value

    def validate_first_name(self, value):
        if not value.strip():
            raise serializers.ValidationError("First name cannot be empty.")
        return value

class AppointmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Appointment
        fields = '__all__'

    def validate_status(self, value):
        if value not in ['Scheduled', 'Completed', 'Cancelled']:
            raise serializers.ValidationError("Invalid status.")
        return value

    def validate_date_time(self, value):
        if value < timezone.now():
            raise serializers.ValidationError("Appointment cannot be in the past.")
        return value

    def validate(self, data):
        # Example: prevent double-booking doctor for the same time
        if Appointment.objects.filter(doctor=data['doctor'], date_time=data['date_time']).exclude(pk=self.instance.pk if self.instance else None).exists():
            raise serializers.ValidationError("Doctor already has an appointment at this time.")
        return data

class BillingSerializer(serializers.ModelSerializer):
    class Meta:
        model = Billing
        fields = '__all__'
        read_only_fields = ('consultation_fee', 'total_fee')

    def validate(self, data):
        if data['consultation_fee'] < 0 or data['medicine_fee'] < 0:
            raise serializers.ValidationError("Fees must be non-negative numbers.")
        if abs(data['total_fee'] - (data['consultation_fee'] + data['medicine_fee'])) > 0.01:
            raise serializers.ValidationError("Total fee must be sum of consultation and medicine fees.")
        return data
