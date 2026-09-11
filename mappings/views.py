from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404
from .models import PatientDoctorMapping
from .serializers import PatientDoctorMappingSerializer, PatientDoctorMappingCreateSerializer
from patients.models import Patient
from doctors.serializers import DoctorSerializer


class MappingListCreateView(APIView):
    """
    POST /api/mappings/ - Assign a doctor to a patient.
    GET  /api/mappings/ - Retrieve all patient-doctor mappings.
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        # Retrieve all mappings for patients owned by the current user
        # (or all mappings if the user is a superuser/staff)
        if request.user.is_staff:
            mappings = PatientDoctorMapping.objects.all()
        else:
            mappings = PatientDoctorMapping.objects.filter(patient__created_by=request.user)

        serializer = PatientDoctorMappingSerializer(mappings, many=True)
        return Response({
            'count': mappings.count(),
            'mappings': serializer.data
        }, status=status.HTTP_200_OK)

    def post(self, request):
        serializer = PatientDoctorMappingCreateSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            mapping = serializer.save()
            detailed_data = PatientDoctorMappingSerializer(mapping).data
            return Response({
                'message': 'Doctor assigned to patient successfully.',
                'mapping': detailed_data
            }, status=status.HTTP_201_CREATED)
        return Response({
            'message': 'Failed to create patient-doctor mapping.',
            'errors': serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)


class PatientDoctorsOrMappingDetailView(APIView):
    """
    Handles both:
    - GET    /api/mappings/<patient_id>/ - Get all doctors assigned to a specific patient.
    - DELETE /api/mappings/<id>/         - Remove a doctor from a patient (delete mapping).
    """
    permission_classes = [IsAuthenticated]

    def get(self, request, pk):
        """
        GET /api/mappings/<patient_id>/
        Retrieve all doctors assigned to the specified patient.
        """
        try:
            patient = Patient.objects.get(pk=pk)
        except Patient.DoesNotExist:
            return Response({
                'message': f'Patient with ID {pk} does not exist.'
            }, status=status.HTTP_404_NOT_FOUND)

        # Ensure user can only view mappings for their own patient
        if patient.created_by != request.user and not request.user.is_staff:
            return Response({
                'message': 'You do not have permission to view mappings for this patient.'
            }, status=status.HTTP_403_FORBIDDEN)

        mappings = PatientDoctorMapping.objects.filter(patient=patient).select_related('doctor')
        doctors = [m.doctor for m in mappings]

        return Response({
            'patient_id': patient.id,
            'patient_name': patient.name,
            'assigned_doctors_count': len(doctors),
            'doctors': DoctorSerializer(doctors, many=True).data,
            'mappings': PatientDoctorMappingSerializer(mappings, many=True).data
        }, status=status.HTTP_200_OK)

    def delete(self, request, pk):
        """
        DELETE /api/mappings/<id>/
        Remove a doctor from a patient by deleting the mapping record with ID = pk.
        Also supports passing ?doctor_id=<id> if pk is treated as patient_id.
        """
        # First attempt: lookup by mapping primary key
        mapping = PatientDoctorMapping.objects.filter(pk=pk).first()

        # Second attempt: check if pk is patient_id and doctor_id is provided in query params
        doctor_id = request.query_params.get('doctor_id')
        if not mapping and doctor_id:
            mapping = PatientDoctorMapping.objects.filter(patient_id=pk, doctor_id=doctor_id).first()

        if not mapping:
            return Response({
                'message': f'Patient-Doctor mapping with ID {pk} does not exist.'
            }, status=status.HTTP_404_NOT_FOUND)

        # Check ownership
        if mapping.patient.created_by != request.user and not request.user.is_staff:
            return Response({
                'message': 'You do not have permission to remove this mapping.'
            }, status=status.HTTP_403_FORBIDDEN)

        patient_name = mapping.patient.name
        doctor_name = mapping.doctor.name
        mapping_id = mapping.id
        mapping.delete()

        return Response({
            'message': f'Mapping ID {mapping_id} removed successfully: Dr. {doctor_name} is no longer assigned to patient {patient_name}.'
        }, status=status.HTTP_200_OK)
