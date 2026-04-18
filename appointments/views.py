from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import action
from datetime import datetime, timedelta
from django.shortcuts import get_object_or_404
from django.core.mail import send_mail
from doctors.models import Doctor
from .models import Appointment
from .serializers import AppointmentSerializer, NotificationSerializer
from .permissions import IsDoctor, IsPatient
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework.parsers import MultiPartParser, FormParser
from .serializers import PrescriptionUploadSerializer
from django.core.mail import EmailMessage
from .models import Notification 


class AppointmentViewSet(viewsets.ModelViewSet):
    queryset = Appointment.objects.all()
    serializer_class = AppointmentSerializer
    permission_classes = [IsAuthenticated]

    # FILTERING (mine=true)
    def get_queryset(self):
        user = self.request.user
        queryset = super().get_queryset()

        mine = self.request.query_params.get('mine')

        if mine == 'true':
            if user.role == 'PATIENT':
                return queryset.filter(patient=user)
            elif user.role == 'DOCTOR':
                return queryset.filter(doctor__user=user)

        return queryset

    # Auto assign patient
    def perform_create(self, serializer):
        appointment = serializer.save(patient=self.request.user)

        if appointment.patient.email:
            send_mail(
                'Appointment Booked',
                f'Hi, Hope you are fine. We are pleased to inform you that your appointment with Dr. {appointment.doctor} on {appointment.date} at {appointment.time} is booked.',
                'shibino.developer@gmail.com',
                [appointment.patient.email],
                fail_silently=False,
            )
        
        # 🔔 Notify Doctor
        Notification.objects.create(
            user=appointment.doctor.user,
            message=f"New appointment booked by {appointment.patient} on {appointment.date} at {appointment.time}"
        )
        # Notify Patient
        Notification.objects.create(
            user=appointment.patient,
            message=f"Your appointment with Dr. {appointment.doctor} is booked successfully"
        )

    # AVAILABLE SLOTS
    @action(detail=False, methods=['get'])
    def available_slots(self, request):
        doctor_id = request.query_params.get('doctor')
        date = request.query_params.get('date')

        if not doctor_id or not date:
            return Response({"error": "doctor and date required"}, status=400)

        doctor = get_object_or_404(Doctor, id=doctor_id)

        start = datetime.combine(datetime.strptime(date, "%Y-%m-%d"), doctor.available_from)
        end = datetime.combine(datetime.strptime(date, "%Y-%m-%d"), doctor.available_to)

        slots = []
        current = start

        while current < end:
            slot_time = current.time()

            if not Appointment.objects.filter(
                doctor=doctor,
                date=date,
                time=slot_time
            ).exists():
                slots.append(slot_time.strftime("%H:%M"))

            current += timedelta(minutes=30)

        return Response({"available_slots": slots})

    # APPROVE (Doctor only)
    @action(detail=True, methods=['post'], permission_classes=[IsDoctor])
    def approve(self, request, pk=None):
        appointment = self.get_object()
        appointment.status = 'APPROVED'
        appointment.save()

        if appointment.patient.email:
            send_mail(
                'Appointment Approved',
                f'Your appointment on {appointment.date} at {appointment.time} has been approved.',
                'shibino.developer@gmail.com',
                [appointment.patient.email],
                fail_silently=False,
            )

        return Response({'status': 'approved'})

    # CANCEL (Patient only)
    @action(detail=True, methods=['post'], permission_classes=[IsPatient])
    def cancel(self, request, pk=None):
        appointment = self.get_object()
        appointment.status = 'CANCELLED'
        appointment.save()

        if appointment.patient.email:
            send_mail(
                'Appointment Cancelled',
                f'Your appointment on {appointment.date} at {appointment.time} has been cancelled.',
                'shibino.developer@gmail.com',
                [appointment.patient.email],
                fail_silently=False,
            )

        return Response({'status': 'cancelled'})

    @swagger_auto_schema(operation_description="Doctor dashboard data")
    @action(detail=False, methods=['get'], permission_classes=[IsDoctor])
    def dashboard(self, request):
        user = request.user
        today = datetime.now().date()

        doctor = Doctor.objects.get(user=user)

        today_appointments = Appointment.objects.filter(
            doctor=doctor,
            date=today
        )

        pending_appointments = Appointment.objects.filter(
            doctor=doctor,
            status='PENDING'
        )

        return Response({
            "today_count": today_appointments.count(),
            "pending_count": pending_appointments.count(),
            "today_appointments": AppointmentSerializer(today_appointments, many=True).data
        })
    
    @swagger_auto_schema(manual_parameters=[openapi.Parameter('prescription', openapi.IN_FORM, type=openapi.TYPE_FILE, required=True, description="Upload prescription file")])
    @action(detail=True, methods=['post'], parser_classes=[MultiPartParser, FormParser], permission_classes=[IsDoctor])
    
    def upload_prescription(self, request, pk=None):
        appointment = self.get_object()

        file = request.FILES.get('prescription')

        if not file:
            return Response({"error": "No file uploaded"}, status=400)

    # Save file
        appointment.prescription = file
        appointment.save()

    # 📧 SEND EMAIL WITH ATTACHMENT
        email = EmailMessage(
            subject="Prescription Uploaded",
            body=f"Hello,\n\nYour prescription for appointment on {appointment.date} at {appointment.time} is attached.\n\nGet well soon!",
            from_email="shibino.developer@gmail.com",
            to=[appointment.patient.email],
        )
        
        # Attach file
        email.attach_file(appointment.prescription.path)
        print("EMAIL FUNCTION CALLED")
        # Send email
        email.send()

        return Response({
            "message": "Prescription uploaded and email sent successfully"
        })

class NotificationViewSet(viewsets.ModelViewSet):
    serializer_class = NotificationSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Notification.objects.filter(user=self.request.user).order_by('-created_at')