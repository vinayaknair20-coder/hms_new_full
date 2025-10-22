# admin_app/management/commands/populate_db.py
from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta
from admin_app.models import User, Specialization, Staff, Doctor
from receptionist_app.models import Patient, Appointment
from pharmacist_app.models import Medicine
from lab_technician_app.models import LabTest


class Command(BaseCommand):
    help = 'Populate database with sample data'

    def handle(self, *args, **kwargs):
        self.stdout.write(self.style.SUCCESS('Starting database population...'))
        
        # Check and create admin user
        if not User.objects.filter(username='admin').exists():
            admin_user = User.objects.create_user(
                username='admin',
                password='admin123',
                role='Admin',
                first_name='System',
                last_name='Admin',
                email='admin@hospital.com'
            )
            self.stdout.write('✓ Created admin user')
        else:
            admin_user = User.objects.get(username='admin')
            self.stdout.write('⚠ Admin user already exists')
        
        # Create specializations
        if Specialization.objects.count() == 0:
            cardiology = Specialization.objects.create(name='Cardiology')
            pediatrics = Specialization.objects.create(name='Pediatrics')
            general = Specialization.objects.create(name='General Medicine')
            self.stdout.write('✓ Created 3 specializations')
        else:
            cardiology = Specialization.objects.first()
            self.stdout.write('⚠ Specializations already exist')
        
        # Create doctor users
        if not User.objects.filter(username='doctor1').exists():
            doc1_user = User.objects.create_user(
                username='doctor1',
                password='doc123',
                role='Doctor',
                first_name='Dr. John',
                last_name='Smith'
            )
            doctor1 = Doctor.objects.create(
                user=doc1_user,
                specialization=cardiology,
                experience=15,
                consultation_fee=1000.00
            )
            self.stdout.write('✓ Created doctor1')
        else:
            self.stdout.write('⚠ doctor1 already exists')
        
        # Create receptionist
        if not User.objects.filter(username='receptionist1').exists():
            recep_user = User.objects.create_user(
                username='receptionist1',
                password='recep123',
                role='Receptionist',
                first_name='Sarah',
                last_name='Johnson'
            )
            receptionist = Staff.objects.create(
                user=recep_user,
                dob='1990-05-15',
                phone='1234567890',
                blood_group='A+',
                hire_date='2020-01-15',
                address='123 Main St'
            )
            self.stdout.write('✓ Created receptionist1')
        else:
            self.stdout.write('⚠ receptionist1 already exists')
        
        # Create pharmacist
        if not User.objects.filter(username='pharmacist1').exists():
            pharm_user = User.objects.create_user(
                username='pharmacist1',
                password='pharm123',
                role='Pharmacist',
                first_name='Robert',
                last_name='Brown'
            )
            pharmacist = Staff.objects.create(
                user=pharm_user,
                dob='1988-03-12',
                phone='1234567892',
                blood_group='O+',
                hire_date='2019-06-01',
                address='789 Elm St'
            )
            self.stdout.write('✓ Created pharmacist1')
        else:
            self.stdout.write('⚠ pharmacist1 already exists')
        
        # Create lab technician
        if not User.objects.filter(username='labtech1').exists():
            lab_user = User.objects.create_user(
                username='labtech1',
                password='lab123',
                role='LabTechnician',
                first_name='Michael',
                last_name='Chen'
            )
            labtech = Staff.objects.create(
                user=lab_user,
                dob='1989-07-18',
                phone='1234567894',
                blood_group='A-',
                hire_date='2019-11-20',
                address='654 Maple Dr'
            )
            self.stdout.write('✓ Created labtech1')
        else:
            self.stdout.write('⚠ labtech1 already exists')
        
        # Create sample patients if none exist
        if Patient.objects.count() < 3:
            patient_data = [
                ('Raj', 'Kumar', '1985-06-15', 'Male', '9876543210', 'AB+', '123 MG Road'),
                ('Priya', 'Sharma', '1990-03-20', 'Female', '9876543211', 'O+', '456 Park St'),
                ('Amit', 'Patel', '1982-11-08', 'Male', '9876543212', 'B+', '789 Beach Rd'),
            ]
            
            for first, last, dob, gender, phone, blood_group, address in patient_data:
                Patient.objects.create(
                    first_name=first,
                    last_name=last,
                    dob=dob,
                    gender=gender,
                    phone=phone,
                    address=address,
                    emergency_contact=phone,
                    blood_group=blood_group,
                    medical_history='Routine checkup'
                )
            self.stdout.write('✓ Created 3 patients')
        else:
            self.stdout.write('⚠ Patients already exist')
        
        # Create medicines if none exist
        if Medicine.objects.count() < 3:
            medicine_data = [
                ('Paracetamol 500mg', 100, 5.00),
                ('Amoxicillin 250mg', 200, 15.00),
                ('Ibuprofen 400mg', 150, 8.00),
            ]
            
            for name, stock, price in medicine_data:
                Medicine.objects.create(
                    name=name,
                    stock=stock,
                    price_per_unit=price,
                    reorder_level=20,
                    manufacturer='Pharma Corp',
                    expiry_date=(timezone.now() + timedelta(days=730)).date(),
                    description='Standard medication'
                )
            self.stdout.write('✓ Created 3 medicines')
        else:
            self.stdout.write('⚠ Medicines already exist')
        
        # Create lab tests if none exist
        if LabTest.objects.count() < 3:
            test_data = [
                ('Complete Blood Count (CBC)', 4000, 11000, 'cells/mm³', 350),
                ('Blood Sugar (Fasting)', 70, 100, 'mg/dL', 200),
                ('Hemoglobin', 12, 16, 'g/dL', 150),
            ]
            
            for name, low, high, unit, price in test_data:
                LabTest.objects.create(
                    test_name=name,
                    low_range=low,
                    high_range=high,
                    unit=unit,
                    price=price,
                    description=f'{name} - Standard test',
                    is_active=True
                )
            self.stdout.write('✓ Created 3 lab tests')
        else:
            self.stdout.write('⚠ Lab tests already exist')
        
        self.stdout.write(self.style.SUCCESS('\n✅ Database population complete!\n'))
        self.stdout.write('='*50)
        self.stdout.write('🔐 LOGIN CREDENTIALS:')
        self.stdout.write('='*50)
        self.stdout.write('Admin: admin / admin123')
        self.stdout.write('Doctor: doctor1 / doc123')
        self.stdout.write('Receptionist: receptionist1 / recep123')
        self.stdout.write('Pharmacist: pharmacist1 / pharm123')
        self.stdout.write('Lab Tech: labtech1 / lab123')
        self.stdout.write('='*50)
