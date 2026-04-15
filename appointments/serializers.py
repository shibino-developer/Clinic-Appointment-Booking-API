from rest_framework import serializers
from .models import Appointment


class AppointmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Appointment
        fields = '__all__'

    def validate(self, data):
        doctor = data.get('doctor')
        time = data.get('time')

        if doctor and time:
            if not (doctor.available_from <= time <= doctor.available_to):
                raise serializers.ValidationError("Doctor not available at this time")

        return data