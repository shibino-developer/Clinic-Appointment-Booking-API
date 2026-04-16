from rest_framework import serializers
from .models import Doctor

class DoctorSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source='user.username')
    email = serializers.EmailField(source='user.email')

    class Meta:
        model = Doctor
        fields = ['id', 'username', 'email', 'specialization', 'available_from', 'available_to']