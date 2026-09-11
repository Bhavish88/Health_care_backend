from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from rest_framework import status
from .models import Doctor

User = get_user_model()


class DoctorAPITests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            name='Hospital Admin',
            email='admin@hospital.com',
            password='Password123'
        )
        self.client.force_authenticate(user=self.user)

        self.doctor_payload = {
            'name': 'Gregory House',
            'specialization': 'Diagnostic Medicine',
            'email': 'house@hospital.com',
            'phone': '1234567890',
            'experience_years': 20
        }

    def test_create_doctor_success(self):
        response = self.client.post('/api/doctors/', self.doctor_payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['doctor']['name'], 'Gregory House')
        self.assertEqual(response.data['doctor']['specialization'], 'Diagnostic Medicine')

    def test_create_doctor_duplicate_email(self):
        self.client.post('/api/doctors/', self.doctor_payload, format='json')
        duplicate_payload = self.doctor_payload.copy()
        duplicate_payload['name'] = 'Another Doctor'
        response = self.client.post('/api/doctors/', duplicate_payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('email', response.data['errors'])

    def test_list_doctors(self):
        Doctor.objects.create(**self.doctor_payload)
        response = self.client.get('/api/doctors/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 1)

    def test_retrieve_doctor_detail(self):
        doctor = Doctor.objects.create(**self.doctor_payload)
        response = self.client.get(f'/api/doctors/{doctor.id}/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['name'], 'Gregory House')

    def test_update_doctor(self):
        doctor = Doctor.objects.create(**self.doctor_payload)
        update_data = {
            'name': 'Gregory House, MD',
            'specialization': 'Nephrology & Diagnostics',
            'email': 'house@hospital.com',
            'phone': '9876543210',
            'experience_years': 25
        }
        response = self.client.put(f'/api/doctors/{doctor.id}/', update_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['doctor']['name'], 'Gregory House, MD')
        self.assertEqual(response.data['doctor']['experience_years'], 25)

    def test_delete_doctor(self):
        doctor = Doctor.objects.create(**self.doctor_payload)
        response = self.client.delete(f'/api/doctors/{doctor.id}/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertFalse(Doctor.objects.filter(id=doctor.id).exists())
