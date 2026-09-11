from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from .serializers import RegisterSerializer, LoginSerializer, UserSerializer


class RegisterView(APIView):
    """
    POST /api/auth/register/
    Registers a new user with name, email, and password.
    Public endpoint.
    """
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            return Response({
                'message': 'User registered successfully.',
                'user': UserSerializer(user).data
            }, status=status.HTTP_201_CREATED)
        return Response({
            'message': 'Registration failed. Please correct the errors below.',
            'errors': serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)


class LoginView(APIView):
    """
    POST /api/auth/login/
    Logs in an existing user with email and password, returning JWT access & refresh tokens.
    Public endpoint.
    """
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        if serializer.is_valid():
            validated_data = serializer.validated_data
            user = validated_data['user']
            return Response({
                'message': 'Login successful.',
                'tokens': {
                    'access': validated_data['access'],
                    'refresh': validated_data['refresh']
                },
                'user': UserSerializer(user).data
            }, status=status.HTTP_200_OK)
        return Response({
            'message': 'Login failed.',
            'errors': serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)
