from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404
from .models import Patient
from .serializers import PatientSerializer
from .permissions import IsPatientOwner


class PatientListCreateView(APIView):
    """
    POST /api/patients/ - Add a new patient (Authenticated users only).
    GET  /api/patients/ - Retrieve all patients created by the authenticated user.
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        # Retrieve all patients created by the authenticated user
        patients = Patient.objects.filter(created_by=request.user)
        serializer = PatientSerializer(patients, many=True)
        return Response({
            'count': patients.count(),
            'patients': serializer.data
        }, status=status.HTTP_200_OK)

    def post(self, request):
        # Add a new patient created by the current user
        serializer = PatientSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(created_by=request.user)
            return Response({
                'message': 'Patient record created successfully.',
                'patient': serializer.data
            }, status=status.HTTP_201_CREATED)
        return Response({
            'message': 'Failed to create patient record.',
            'errors': serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)


class PatientDetailView(APIView):
    """
    GET    /api/patients/<id>/ - Get details of a specific patient.
    PUT    /api/patients/<id>/ - Update patient details.
    DELETE /api/patients/<id>/ - Delete a patient record.
    """
    permission_classes = [IsAuthenticated, IsPatientOwner]

    def get_object(self, pk, user):
        try:
            patient = Patient.objects.get(pk=pk)
        except Patient.DoesNotExist:
            return None, Response({
                'message': f'Patient with ID {pk} does not exist.'
            }, status=status.HTTP_404_NOT_FOUND)

        # Ensure only the owner can access their patient record
        if patient.created_by != user:
            return None, Response({
                'message': 'You do not have permission to access this patient record.'
            }, status=status.HTTP_403_FORBIDDEN)

        return patient, None

    def get(self, request, pk):
        patient, error_response = self.get_object(pk, request.user)
        if error_response:
            return error_response

        serializer = PatientSerializer(patient)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def put(self, request, pk):
        patient, error_response = self.get_object(pk, request.user)
        if error_response:
            return error_response

        # Allow partial updates as well for flexibility
        partial = request.method == 'PATCH' or request.query_params.get('partial', 'false').lower() == 'true'
        serializer = PatientSerializer(patient, data=request.data, partial=partial)
        if serializer.is_valid():
            serializer.save()
            return Response({
                'message': 'Patient updated successfully.',
                'patient': serializer.data
            }, status=status.HTTP_200_OK)
        return Response({
            'message': 'Failed to update patient record.',
            'errors': serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)

    def patch(self, request, pk):
        patient, error_response = self.get_object(pk, request.user)
        if error_response:
            return error_response

        serializer = PatientSerializer(patient, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response({
                'message': 'Patient updated successfully.',
                'patient': serializer.data
            }, status=status.HTTP_200_OK)
        return Response({
            'message': 'Failed to update patient record.',
            'errors': serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        patient, error_response = self.get_object(pk, request.user)
        if error_response:
            return error_response

        patient_name = patient.name
        patient.delete()
        return Response({
            'message': f'Patient "{patient_name}" (ID: {pk}) deleted successfully.'
        }, status=status.HTTP_200_OK)
