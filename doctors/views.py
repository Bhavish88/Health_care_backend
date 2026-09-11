from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .models import Doctor
from .serializers import DoctorSerializer


class DoctorListCreateView(APIView):
    """
    POST /api/doctors/ - Add a new doctor (Authenticated users only).
    GET  /api/doctors/ - Retrieve all doctors.
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        doctors = Doctor.objects.all()
        serializer = DoctorSerializer(doctors, many=True)
        return Response({
            'count': doctors.count(),
            'doctors': serializer.data
        }, status=status.HTTP_200_OK)

    def post(self, request):
        serializer = DoctorSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({
                'message': 'Doctor registered successfully.',
                'doctor': serializer.data
            }, status=status.HTTP_201_CREATED)
        return Response({
            'message': 'Failed to add doctor.',
            'errors': serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)


class DoctorDetailView(APIView):
    """
    GET    /api/doctors/<id>/ - Get details of a specific doctor.
    PUT    /api/doctors/<id>/ - Update doctor details.
    DELETE /api/doctors/<id>/ - Delete a doctor record.
    """
    permission_classes = [IsAuthenticated]

    def get_object(self, pk):
        try:
            return Doctor.objects.get(pk=pk), None
        except Doctor.DoesNotExist:
            return None, Response({
                'message': f'Doctor with ID {pk} does not exist.'
            }, status=status.HTTP_404_NOT_FOUND)

    def get(self, request, pk):
        doctor, error_response = self.get_object(pk)
        if error_response:
            return error_response
        serializer = DoctorSerializer(doctor)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def put(self, request, pk):
        doctor, error_response = self.get_object(pk)
        if error_response:
            return error_response

        partial = request.method == 'PATCH' or request.query_params.get('partial', 'false').lower() == 'true'
        serializer = DoctorSerializer(doctor, data=request.data, partial=partial)
        if serializer.is_valid():
            serializer.save()
            return Response({
                'message': 'Doctor details updated successfully.',
                'doctor': serializer.data
            }, status=status.HTTP_200_OK)
        return Response({
            'message': 'Failed to update doctor details.',
            'errors': serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)

    def patch(self, request, pk):
        doctor, error_response = self.get_object(pk)
        if error_response:
            return error_response

        serializer = DoctorSerializer(doctor, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response({
                'message': 'Doctor details updated successfully.',
                'doctor': serializer.data
            }, status=status.HTTP_200_OK)
        return Response({
            'message': 'Failed to update doctor details.',
            'errors': serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        doctor, error_response = self.get_object(pk)
        if error_response:
            return error_response

        doctor_name = doctor.name
        doctor.delete()
        return Response({
            'message': f'Doctor "{doctor_name}" (ID: {pk}) deleted successfully.'
        }, status=status.HTTP_200_OK)
