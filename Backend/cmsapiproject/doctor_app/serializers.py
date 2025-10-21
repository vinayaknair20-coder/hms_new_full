from rest_framework import serializers
from .models import Consultation, Prescription

class ConsultationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Consultation
        fields = '__all__'

    def validate(self, data):
        if not data.get('symptoms') or not data.get('diagnosis'):
            raise serializers.ValidationError("Symptoms and diagnosis are required.")
        return data

    def validate_notes(self, value):
        if len(value) > 1000:
            raise serializers.ValidationError("Notes are too long.")
        return value

class PrescriptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Prescription
        fields = '__all__'

    def validate_prescription_notes(self, value):
        if len(value) > 1000:
            raise serializers.ValidationError("Prescription notes are too long.")
        return value

    def validate(self, data):
        for f in ['dosage', 'frequency', 'duration']:
            if not data.get(f):
                raise serializers.ValidationError(f"{f.capitalize()} is required!")
        return data