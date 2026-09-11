from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from rest_framework import status
from .models import Patient

User = get_user_model()


class PatientAPITests(TestCase):
    def setUp(self):
        self.client = APIClient()

        # Create two distinct users to verify isolation
        self.user_a = User.objects.create_user(
            name='User A',
            email='user.a@example.com',
            password='Password123'
        )
        self.user_b = User.objects.create_user(
            name='User B',
            email='user.b@example.com',
            password='Password123'
        )

        # Authenticate as user_a by default
        self.client.force_authenticate(user=self.user_a)

        self.patient_payload = {
            'name': 'John Doe',
            'age': 35,
            'gender': 'Male',
            'contact_number': '1234567890',
            'address': '123 Medical Way',
            'medical_history': 'No allergies known'
        }

    def test_unauthenticated_request_rejected(self):
        self.client.force_authenticate(user=None)
        response = self.client.get('/api/patients/')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_create_patient_success(self):
        response = self.client.post('/api/patients/', self.patient_payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['patient']['name'], 'John Doe')
        self.assertEqual(response.data['patient']['created_by'], self.user_a.id)

    def test_list_patients_only_returns_own_records(self):
        # Patient for User A
        Patient.objects.create(
            name='User A Patient',
            age=25,
            gender='Female',
            contact_number='1112223333',
            created_by=self.user_a
        )
        # Patient for User B
        Patient.objects.create(
            name='User B Patient',
            age=40,
            gender='Male',
            contact_number='4445556666',
            created_by=self.user_b
        )

        response = self.client.get('/api/patients/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 1)
        self.assertEqual(response.data['patients'][0]['name'], 'User A Patient')

    def test_retrieve_patient_detail(self):
        patient = Patient.objects.create(
            name='Jane Smith',
            age=29,
            gender='Female',
            contact_number='9876543210',
            created_by=self.user_a
        )
        response = self.client.get(f'/api/patients/{patient.id}/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['name'], 'Jane Smith')

    def test_user_cannot_access_another_users_patient(self):
        patient_b = Patient.objects.create(
            name='Patient Belonging to B',
            age=50,
            gender='Other',
            contact_number='5555555555',
            created_by=self.user_b
        )
        # User A tries to get Patient B
        response = self.client.get(f'/api/patients/{patient_b.id}/')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_update_patient(self):
        patient = Patient.objects.create(
            name='Initial Name',
            age=20,
            gender='Male',
            contact_number='1234567890',
            created_by=self.user_a
        )
        update_data = {
            'name': 'Updated Name',
            'age': 21,
            'gender': 'Male',
            'contact_number': '1234567890',
            'medical_history': 'Updated history'
        }
        response = self.client.put(f'/api/patients/{patient.id}/', update_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['patient']['name'], 'Updated Name')
        self.assertEqual(response.data['patient']['age'], 21)

    def test_delete_patient(self):
        patient = Patient.objects.create(
            name='To Delete',
            age=45,
            gender='Female',
            contact_number='1234567890',
            created_by=self.user_a
        )
        response = self.client.delete(f'/api/patients/{patient.id}/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertFalse(Patient.objects.filter(id=patient.id).exists())
