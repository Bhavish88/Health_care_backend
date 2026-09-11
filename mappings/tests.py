from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from rest_framework import status
from patients.models import Patient
from doctors.models import Doctor
from .models import PatientDoctorMapping

User = get_user_model()


class MappingAPITests(TestCase):
    def setUp(self):
        self.client = APIClient()

        self.user_a = User.objects.create_user(
            name='Doctor User A',
            email='user_a@example.com',
            password='Password123'
        )
        self.user_b = User.objects.create_user(
            name='Doctor User B',
            email='user_b@example.com',
            password='Password123'
        )

        self.client.force_authenticate(user=self.user_a)

        self.patient = Patient.objects.create(
            name='Alice Patient',
            age=40,
            gender='Female',
            contact_number='1234567890',
            created_by=self.user_a
        )

        self.doctor_1 = Doctor.objects.create(
            name='Dr. Stephen Strange',
            specialization='Neurosurgeon',
            email='strange@marvel.com',
            phone='1112223333',
            experience_years=15
        )

        self.doctor_2 = Doctor.objects.create(
            name='Dr. Leonard McCoy',
            specialization='Chief Medical Officer',
            email='mccoy@starfleet.com',
            phone='4445556666',
            experience_years=22
        )

    def test_assign_doctor_to_patient_success(self):
        payload = {
            'patient': self.patient.id,
            'doctor': self.doctor_1.id,
            'notes': 'Primary consultation'
        }
        response = self.client.post('/api/mappings/', payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['mapping']['patient'], self.patient.id)
        self.assertEqual(response.data['mapping']['doctor'], self.doctor_1.id)

    def test_duplicate_mapping_rejected(self):
        PatientDoctorMapping.objects.create(
            patient=self.patient,
            doctor=self.doctor_1,
            notes='First assignment'
        )
        payload = {
            'patient': self.patient.id,
            'doctor': self.doctor_1.id
        }
        response = self.client.post('/api/mappings/', payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_cannot_assign_doctor_to_another_users_patient(self):
        patient_b = Patient.objects.create(
            name='Bob Patient',
            age=30,
            gender='Male',
            contact_number='9998887777',
            created_by=self.user_b
        )
        payload = {
            'patient': patient_b.id,
            'doctor': self.doctor_1.id
        }
        response = self.client.post('/api/mappings/', payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_list_all_mappings(self):
        PatientDoctorMapping.objects.create(patient=self.patient, doctor=self.doctor_1)
        response = self.client.get('/api/mappings/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 1)

    def test_get_doctors_assigned_to_patient(self):
        PatientDoctorMapping.objects.create(patient=self.patient, doctor=self.doctor_1)
        PatientDoctorMapping.objects.create(patient=self.patient, doctor=self.doctor_2)

        response = self.client.get(f'/api/mappings/{self.patient.id}/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['patient_id'], self.patient.id)
        self.assertEqual(response.data['assigned_doctors_count'], 2)
        doctor_names = [d['name'] for d in response.data['doctors']]
        self.assertIn('Dr. Stephen Strange', doctor_names)
        self.assertIn('Dr. Leonard McCoy', doctor_names)

    def test_delete_mapping(self):
        mapping = PatientDoctorMapping.objects.create(patient=self.patient, doctor=self.doctor_1)
        response = self.client.delete(f'/api/mappings/{mapping.id}/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertFalse(PatientDoctorMapping.objects.filter(id=mapping.id).exists())
