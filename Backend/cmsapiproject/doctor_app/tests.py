from django.test import TestCase
from doctor_app.models import Consultation, Prescription
from admin_app.models import User, Doctor
from receptionist_app.models import Patient, Appointment, Staff

class DoctorAppTests(TestCase):
    def setUp(self):
        # Doctor & patient
        self.doctor_user = User.objects.create_user(username="doc2", password="docpass2", role="Doctor")
        self.doctor = Doctor.objects.create(user=self.doctor_user, specialization=None, experience=2, consultation_fee=400.00)
        self.patient = Patient.objects.create(
            first_name="Joe", last_name="Bloggs", dob="2000-02-02",
            gender="male", phone="8888888888", address="456 Market",
            emergency_contact="7777777777", medical_history=""
        )
        # Receptionist/Staff for Appointment
        self.staff_user = User.objects.create_user(username="rec3", password="rec3pass", role="Receptionist")
        self.staff = Staff.objects.create(
            user=self.staff_user, dob="1988-09-23", phone="9212345678",
            blood_group="A-", hire_date="2019-03-10", address="Reception"
        )
        self.appointment = Appointment.objects.create(
            patient=self.patient, doctor=self.doctor, receptionist=self.staff,
            date_time="2023-12-03T09:00:00Z", status="Scheduled"
        )
        self.consultation = Consultation.objects.create(
            appointment=self.appointment, doctor=self.doctor, patient=self.patient,
            symptoms="Cough", diagnosis="Cold", notes="Take rest"
        )
        self.prescription = Prescription.objects.create(
            consultation=self.consultation, doctor=self.doctor,
            dosage="10ml", frequency="2x daily", duration="5 days",
            prescription_notes="Drink water"
        )

    def test_consultation_fields(self):
        self.assertEqual(self.consultation.diagnosis, "Cold")
        self.assertEqual(self.consultation.patient.first_name, "Joe")

    def test_prescription_fields(self):
        self.assertEqual(self.prescription.dosage, "10ml")
