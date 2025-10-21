from django.test import TestCase
from pharmacist_app.models import Medicine, PrescriptionMedicine, MedicineStockHistory, MedicineBilling
from doctor_app.models import Prescription
from receptionist_app.models import Patient, Appointment
from admin_app.models import User, Staff, Doctor

class PharmacistAppTests(TestCase):
    def setUp(self):
        # Prepare patient, doctor, staff, appointment, prescription
        self.staff_user = User.objects.create_user(username="pharmstaff", password="pharmstaffpass", role="Pharmacist")
        self.staff = Staff.objects.create(
            user=self.staff_user, dob="1980-04-01", phone="9999999999",
            blood_group="B+", hire_date="2022-06-10", address="Pharmacy"
        )
        self.patient = Patient.objects.create(
            first_name="Sam", last_name="Well", dob="1992-11-11",
            gender="male", phone="9222222222", address="Pharma Road",
            emergency_contact="9111111111", medical_history=""
        )
        self.doctor_user = User.objects.create_user(username="docpharm", password="docpharmpass", role="Doctor")
        self.doctor = Doctor.objects.create(
            user=self.doctor_user, specialization=None, experience=1, consultation_fee=200
        )
        self.appointment = Appointment.objects.create(
            patient=self.patient, doctor=self.doctor, receptionist=None,
            date_time="2023-12-10T15:00:00Z", status="Completed"
        )
        # Dummy consultation+prescription
        from doctor_app.models import Consultation
        self.consultation = Consultation.objects.create(
            appointment=self.appointment, doctor=self.doctor, patient=self.patient, symptoms="Test", diagnosis="Test"
        )
        self.prescription = Prescription.objects.create(
            consultation=self.consultation, doctor=self.doctor,
            dosage="5mg", frequency="daily", duration="7",
            prescription_notes="None"
        )
        self.medicine = Medicine.objects.create(name="Paracetamol", description="Painkiller", stock=50, price_per_unit=5.5)
        self.rxmed = PrescriptionMedicine.objects.create(prescription=self.prescription, medicine=self.medicine, quantity=2)
        # simulate that dispensing will be handled when billing is created
        self.stock_history = None
        self.billing = MedicineBilling.objects.create(
            prescription=self.prescription, patient=self.patient,
            created_by=self.staff
        )

    def test_medicine_fields(self):
        self.assertEqual(self.medicine.name, "Paracetamol")
        self.assertEqual(float(self.medicine.price_per_unit), 5.5)

    def test_prescription_medicine_link(self):
        self.assertEqual(self.rxmed.medicine.name, "Paracetamol")

    def test_medicine_billing(self):
        # total should be computed from prescription lines (2 * 5.5 = 11.0)
        self.assertEqual(float(self.billing.total_medicine_fee), 11.0)
        # stock decreased by 2
        med = Medicine.objects.get(pk=self.medicine.pk)
        self.assertEqual(med.stock, 48)
        # a stock history entry should exist for this prescription
        hist = MedicineStockHistory.objects.filter(related_prescription=self.prescription)
        self.assertTrue(hist.exists())
