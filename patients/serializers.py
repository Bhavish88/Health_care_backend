from rest_framework import serializers
from .models import Patient


class PatientSerializer(serializers.ModelSerializer):
    """
    Serializer for the Patient model.
    Handles validation and serialization of patient data.
    'created_by' is automatically populated from the authenticated user.
    """
    created_by_name = serializers.ReadOnlyField(source='created_by.name')
    created_by_email = serializers.ReadOnlyField(source='created_by.email')

    class Meta:
        model = Patient
        fields = [
            'id',
            'name',
            'age',
            'gender',
            'contact_number',
            'address',
            'medical_history',
            'created_by',
            'created_by_name',
            'created_by_email',
            'created_at',
            'updated_at',
        ]
        read_only_fields = ['id', 'created_by', 'created_at', 'updated_at']

    def validate_name(self, value):
        if not value.strip():
            raise serializers.ValidationError("Patient name cannot be blank.")
        return value.strip()

    def validate_age(self, value):
        if value < 0 or value > 150:
            raise serializers.ValidationError("Please provide a realistic age between 0 and 150.")
        return value

    def validate_contact_number(self, value):
        clean_contact = value.strip()
        if not clean_contact:
            raise serializers.ValidationError("Contact number cannot be blank.")
        if len(clean_contact) < 7:
            raise serializers.ValidationError("Contact number must be at least 7 characters long.")
        return clean_contact
