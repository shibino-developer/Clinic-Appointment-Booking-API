from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from .models import Appointment
from .serializers import AppointmentSerializer


class AppointmentViewSet(viewsets.ModelViewSet):
    serializer_class = AppointmentSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user

        if user.role == 'PATIENT':
            return Appointment.objects.filter(patient=user)

        elif user.role == 'DOCTOR':
            return Appointment.objects.filter(doctor__user=user)

        return Appointment.objects.all()

    def perform_create(self, serializer):
        serializer.save(patient=self.request.user)

    def cancel(self, request, pk=None):
        appointment = Appointment.objects.get(pk=pk)

        if appointment.patient != request.user:
            return Response({"error": "Unauthorized"}, status=403)

        appointment.status = 'CANCELLED'
        appointment.save()

        return Response({"message": "Cancelled"})

    def approve(self, request, pk=None):
        appointment = Appointment.objects.get(pk=pk)

        if request.user.role != 'DOCTOR':
            return Response({"error": "Only doctors can approve"}, status=403)

        appointment.status = 'APPROVED'
        appointment.save()

        return Response({"message": "Approved"})