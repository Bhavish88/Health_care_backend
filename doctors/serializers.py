from rest_framework import serializers
from .models import Doctor


class DoctorSerializer(serializers.ModelSerializer):
    """
    Serializer for Doctor model with validation for email uniqueness and field lengths.
    """
    class Meta:
        model = Doctor
        fields = [
            'id',
            'name',
            'specialization',
            'email',
            'phone',
            'experience_years',
            'created_at',
            'updated_at',
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']

    def validate_name(self, value):
        clean_name = value.strip()
        if not clean_name:
            raise serializers.ValidationError("Doctor name cannot be blank.")
        return clean_name

    def validate_specialization(self, value):
        clean_spec = value.strip()
        if not clean_spec:
            raise serializers.ValidationError("Specialization cannot be blank.")
        return clean_spec

    def validate_email(self, value):
        clean_email = value.lower().strip()
        # On update, allow current instance's email
        instance = getattr(self, 'instance', None)
        query = Doctor.objects.filter(email__iexact=clean_email)
        if instance:
            query = query.exclude(pk=instance.pk)
        if query.exists():
            raise serializers.ValidationError("A doctor with this email already exists.")
        return clean_email

    def validate_phone(self, value):
        clean_phone = value.strip()
        if not clean_phone:
            raise serializers.ValidationError("Phone number cannot be blank.")
        if len(clean_phone) < 7:
            raise serializers.ValidationError("Phone number must be at least 7 digits.")
        return clean_phone

    def validate_experience_years(self, value):
        if value < 0 or value > 80:
            raise serializers.ValidationError("Experience years must be between 0 and 80.")
        return value
