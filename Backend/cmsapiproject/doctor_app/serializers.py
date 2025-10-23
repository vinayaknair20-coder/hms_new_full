from rest_framework import serializers
from .models import Consultation, Prescription, MedicinePrescription, TestPrescription
from admin_app.models import Staff
from django.utils import timezone


class MedicinePrescriptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = MedicinePrescription
        fields = '__all__'
        extra_kwargs = {'prescription': {'required': False}}

class TestPrescriptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = TestPrescription
        fields = '__all_'
        extra_kwargs = {'prescription': {'required': False}}

class PrescriptionSerializer(serializers.ModelSerializer):
    patientname = serializers.CharField(source='patient.Patientname', read_only=True)
    doctorname = serializers.CharField(source='doctor.staffname', read_only=True)
    medicines = MedicinePrescriptionSerializer(many=True, source='medicine_prescriptions', read_only=True)
    tests = TestPrescriptionSerializer(many=True, source='test_prescriptions', read_only=True)

    class Meta:
        model = Prescription
        fields = '__all__'
        read_only_fields = ['prescriptionid', 'created_at']

class PrescriptionCreateSerializer(serializers.ModelSerializer):
    medicines = MedicinePrescriptionSerializer(many=True, required=False)
    tests = TestPrescriptionSerializer(many=True, required=False)

    class Meta:
        model = Prescription
        fields = '__all__'

    def create(self, validated_data):
        medicines_data = validated_data.pop('medicines', [])
        tests_data = validated_data.pop('tests', [])
        prescription = Prescription.objects.create(**validated_data)

        for med_data in medicines_data:
            MedicinePrescription.objects.create(prescription=prescription, **med_data)

        for test_data in tests_data:
            TestPrescription.objects.create(prescription=prescription, **test_data)

        return prescription

    def update(self, instance, validated_data):
        medicines_data = validated_data.pop('medicines', [])
        tests_data = validated_data.pop('tests', [])

        # Update Prescription fields
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        # Update medicines
        existing_meds = {m.medicinename: m for m in instance.medicine_prescriptions.all()}
        new_med_names = [item['medicinename'] for item in medicines_data]

        for med_data in medicines_data:
            medname = med_data.get('medicinename')
            if medname in existing_meds:
                med_obj = existing_meds[medname]
                for attr, value in med_data.items():
                    setattr(med_obj, attr, value)
                med_obj.save()
            else:
                MedicinePrescription.objects.create(prescription=instance, **med_data)

        for medname in set(existing_meds) - set(new_med_names):
            existing_meds[medname].delete()

        # Update tests
        existing_tests = {t.testname: t for t in instance.test_prescriptions.all()}
        new_test_names = [item['testname'] for item in tests_data]

        for test_data in tests_data:
            testname = test_data.get('testname')
            if testname in existing_tests:
                test_obj = existing_tests[testname]
                for attr, value in test_data.items():
                    setattr(test_obj, attr, value)
                test_obj.save()
            else:
                TestPrescription.objects.create(prescription=instance, **test_data)

        for testname in set(existing_tests) - set(new_test_names):
            existing_tests[testname].delete()

        return instance




class ConsultationSerializer(serializers.ModelSerializer):
    # Access patient name through appointment → patient
    patientname = serializers.SerializerMethodField()
    patientage = serializers.SerializerMethodField()
    # Assuming doctor is a Staff object, get full name
    doctorname = serializers.SerializerMethodField()
    appointmentid = serializers.IntegerField(source='appointment.appointmentid', read_only=True)

    class Meta:
        model = Consultation
        fields = '__all__'
        read_only_fields = ['consultationid', 'createdat', 'updatedat']

    def get_patientname(self, obj):
        if obj.appointment and obj.appointment.patient:
            return f"{obj.appointment.patient.first_name} {obj.appointment.patient.last_name}"
        return "Unknown"

    def get_patientage(self, obj):
        if obj.appointment and obj.appointment.patient and hasattr(obj.appointment.patient, 'dob'):
            today = timezone.now().date()
            dob = obj.appointment.patient.dob
            return today.year - dob.year - ((today.month, today.day) < (dob.month, dob.day))
        return None

    def get_doctorname(self, obj):
        if obj.doctor:
            # Assuming your Staff model has user with first_name & last_name
            if hasattr(obj.doctor, 'user'):
                return f"{obj.doctor.user.first_name} {obj.doctor.user.last_name}"
            return str(obj.doctor)
        return "Unknown"
