from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.core.mail import send_mail

from .models import Appointment
from .serializers import AppointmentSerializer


class AppointmentViewSet(viewsets.ModelViewSet):
    queryset = Appointment.objects.all()
    serializer_class = AppointmentSerializer
    permission_classes = [IsAuthenticated]

    # 🔍 Filter appointments based on role
    def get_queryset(self):
        user = self.request.user

        if user.role == 'PATIENT':
            return Appointment.objects.filter(patient=user)

        elif user.role == 'DOCTOR':
            return Appointment.objects.filter(doctor__user=user)

        return Appointment.objects.all()  # Admin

    # 📝 Create appointment (Patient only)
    def create(self, request, *args, **kwargs):
        if request.user.role != 'PATIENT':
            return Response(
                {"error": "Only patients can book appointments"},
                status=status.HTTP_403_FORBIDDEN
            )

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        appointment = serializer.save(patient=request.user)

        # 📩 Send email (console backend for now)
        send_mail(
            subject='Appointment Request Submitted',
            message='Your appointment is pending approval.',
            from_email='admin@clinic.com',
            recipient_list=[request.user.email],
            fail_silently=True,
        )

        return Response(serializer.data, status=status.HTTP_201_CREATED)

    # ❌ Cancel appointment
    def cancel(self, request, pk=None):
        try:
            appointment = Appointment.objects.get(pk=pk)
        except Appointment.DoesNotExist:
            return Response({"error": "Not found"}, status=404)

        if appointment.patient != request.user:
            return Response({"error": "Unauthorized"}, status=403)

        appointment.status = 'CANCELLED'
        appointment.save()

        return Response({"message": "Appointment cancelled"})

    # 🔄 Reschedule appointment
    def reschedule(self, request, pk=None):
        try:
            appointment = Appointment.objects.get(pk=pk)
        except Appointment.DoesNotExist:
            return Response({"error": "Not found"}, status=404)

        if appointment.patient != request.user:
            return Response({"error": "Unauthorized"}, status=403)

        new_date = request.data.get("date")
        new_time = request.data.get("time")

        if not new_date or not new_time:
            return Response(
                {"error": "Date and time required"},
                status=400
            )

        appointment.date = new_date
        appointment.time = new_time
        appointment.status = 'RESCHEDULED'
        appointment.save()

        return Response({"message": "Appointment rescheduled"})

    # 👨‍⚕️ Doctor approves appointment
    def approve(self, request, pk=None):
        try:
            appointment = Appointment.objects.get(pk=pk)
        except Appointment.DoesNotExist:
            return Response({"error": "Not found"}, status=404)

        if request.user.role != 'DOCTOR':
            return Response({"error": "Only doctors can approve"}, status=403)

        if appointment.doctor.user != request.user:
            return Response({"error": "Not your patient"}, status=403)

        appointment.status = 'APPROVED'
        appointment.save()

        return Response({"message": "Appointment approved"})