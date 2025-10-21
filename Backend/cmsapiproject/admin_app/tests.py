from django.test import TestCase
from receptionist_app.models import Patient, Appointment, Billing
from admin_app.models import Doctor, Staff, User

class ReceptionistAppTests(TestCase):
    def setUp(self):
        self.staff_user = User.objects.create_user(username="recuser", password="recpass", role="Receptionist")
        self.staff = Staff.objects.create(
            user=self.staff_user, dob="1985-03-15", phone="9123456789",
            blood_group="O+", hire_date="2021-07-01", address="Reception Desk"
        )
        self.patient = Patient.objects.create(
            first_name="Jane", last_name="Doe", dob="1995-05-01", gender="female",
            phone="9876543210", address="123 Main St", emergency_contact="9123456789", medical_history=""
        )
        # Need a Doctor/Doctor user for Appointment
        self.doctor_user = User.objects.create_user(username="doctor2", password="docpass2", role="Doctor")
        self.doctor = Doctor.objects.create(
            user=self.doctor_user, specialization=None, experience=3, consultation_fee=300
        )
        self.appointment = Appointment.objects.create(
            patient=self.patient, doctor=self.doctor, receptionist=self.staff,
            date_time="2023-12-02T11:00:00Z", status="Scheduled"
        )
        self.billing = Billing.objects.create(
            appointment=self.appointment,
            total_fee=600.00, consultation_fee=300.00, medicine_fee=300.00,
            created_by=self.staff, timestamp="2023-12-02T11:30:00Z"
        )

    def test_patient_fields(self):
        self.assertEqual(self.patient.first_name, "Jane")
        self.assertEqual(self.patient.last_name, "Doe")
        self.assertEqual(self.patient.phone, "9876543210")

    def test_appointment_status(self):
        self.assertEqual(self.appointment.status, "Scheduled")

    def test_billing_amount(self):
        self.assertEqual(self.billing.total_fee, 600.00)
