from rest_framework import serializers
from .models import Appointment, Notification


class AppointmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Appointment
        fields = '__all__'
        # read_only_fields = ['patient', 'status']

    def validate(self, data):
        doctor = data.get('doctor')
        date = data.get('date')
        time = data.get('time')

        # Prevent double booking
        if Appointment.objects.filter(
            doctor=doctor,
            date=date,
            time=time
        ).exists():
            raise serializers.ValidationError("This time slot is already booked.")

        # Check doctor availability
        if doctor and time:
            if not (doctor.available_from <= time <= doctor.available_to):
                raise serializers.ValidationError("Doctor not available at this time")

        return data
    
class PrescriptionUploadSerializer(serializers.ModelSerializer):
    class Meta:
        model = Appointment
        fields = ['prescription']


class NotificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notification
        fields = '__all__'