from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from admin_app.models import Staff

# Get the custom User model
User = get_user_model()

class Command(BaseCommand):
    help = 'Creates test users for all roles in the Hospital Management System'

    def handle(self, *args, **kwargs):
        self.stdout.write(self.style.SUCCESS('\n🏥 Creating Test Users for Hospital Management System...\n'))

        # Test users data
        test_users = [
            {
                'username': 'admin',
                'password': 'admin123',
                'email': 'admin@hospital.com',
                'first_name': 'System',
                'last_name': 'Administrator',
                'role': 'Admin',
            },
            {
                'username': 'doctor1',
                'password': 'doctor123',
                'email': 'doctor1@hospital.com',
                'first_name': 'John',
                'last_name': 'Smith',
                'role': 'Doctor',
            },
            {
                'username': 'receptionist1',
                'password': 'reception123',
                'email': 'reception@hospital.com',
                'first_name': 'Sarah',
                'last_name': 'Johnson',
                'role': 'Receptionist',
            },
            {
                'username': 'pharmacist1',
                'password': 'pharma123',
                'email': 'pharmacist@hospital.com',
                'first_name': 'Michael',
                'last_name': 'Brown',
                'role': 'Pharmacist',
            },
            {
                'username': 'labtech1',
                'password': 'labtech123',
                'email': 'labtech@hospital.com',
                'first_name': 'Emily',
                'last_name': 'Davis',
                'role': 'Lab Technician',
            },
        ]

        created_count = 0
        
        for user_data in test_users:
            username = user_data['username']
            
            # Check if user already exists
            if User.objects.filter(username=username).exists():
                self.stdout.write(self.style.WARNING(f'⚠️  User "{username}" already exists. Skipping...'))
                continue

            # Create Django User
            user = User.objects.create_user(
                username=user_data['username'],
                password=user_data['password'],
                email=user_data['email'],
                first_name=user_data['first_name'],
                last_name=user_data['last_name'],
            )

            # Create Staff profile with role
            Staff.objects.create(
                user=user,
                role=user_data['role'],
            )

            created_count += 1
            self.stdout.write(
                self.style.SUCCESS(
                    f'✅ Created {user_data["role"]}: {username} | Password: {user_data["password"]}'
                )
            )

        self.stdout.write(self.style.SUCCESS(f'\n🎉 Successfully created {created_count} test users!\n'))
        
        # Print credentials summary
        self.stdout.write(self.style.SUCCESS('📋 TEST USER CREDENTIALS:\n'))
        self.stdout.write('=' * 60)
        for user_data in test_users:
            self.stdout.write(f"\n{user_data['role']:15} | Username: {user_data['username']:15} | Password: {user_data['password']}")
        self.stdout.write('\n' + '=' * 60)
