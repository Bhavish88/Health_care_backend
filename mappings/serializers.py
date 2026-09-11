from rest_framework import serializers
from .models import PatientDoctorMapping
from patients.models import Patient
from doctors.models import Doctor
from doctors.serializers import DoctorSerializer
from patients.serializers import PatientSerializer


class PatientDoctorMappingSerializer(serializers.ModelSerializer):
    """
    Detailed serializer for reading mappings, including full doctor and patient info.
    """
    patient_details = PatientSerializer(source='patient', read_only=True)
    doctor_details = DoctorSerializer(source='doctor', read_only=True)

    class Meta:
        model = PatientDoctorMapping
        fields = [
            'id',
            'patient',
            'doctor',
            'patient_details',
            'doctor_details',
            'assigned_date',
            'notes',
        ]
        read_only_fields = ['id', 'assigned_date']


class PatientDoctorMappingCreateSerializer(serializers.ModelSerializer):
    """
    Serializer for creating/assigning a doctor to a patient.
    Enforces that:
    1. The patient belongs to the authenticated user.
    2. The doctor is not already assigned to the patient.
    """
    class Meta:
        model = PatientDoctorMapping
        fields = ['id', 'patient', 'doctor', 'notes', 'assigned_date']
        read_only_fields = ['id', 'assigned_date']

    def validate(self, attrs):
        patient = attrs.get('patient')
        doctor = attrs.get('doctor')
        request = self.context.get('request')

        # Verify that the patient belongs to the authenticated user
        if request and hasattr(request, 'user') and request.user.is_authenticated:
            if patient.created_by != request.user:
                raise serializers.ValidationError({
                    'patient': 'You can only assign doctors to patients you created.'
                })

        # Verify duplicate mapping does not exist
        if PatientDoctorMapping.objects.filter(patient=patient, doctor=doctor).exists():
            raise serializers.ValidationError({
                'non_field_errors': [f'Dr. {doctor.name} is already assigned to patient {patient.name}.']
            })

        return attrs
