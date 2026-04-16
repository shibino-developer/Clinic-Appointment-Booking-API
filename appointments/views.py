from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import action
from datetime import datetime, timedelta
from django.shortcuts import get_object_or_404
from doctors.models import Doctor
from .models import Appointment
from .serializers import AppointmentSerializer
from .permissions import IsDoctor, IsPatient
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import action

class AppointmentViewSet(viewsets.ModelViewSet):
    queryset = Appointment.objects.all()
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

        # check if already booked
            if not Appointment.objects.filter(
                doctor=doctor,
                date=date,
                time=slot_time
            ).exists():
                slots.append(slot_time.strftime("%H:%M"))

            current += timedelta(minutes=30)  # 30 min slots

        return Response({"available_slots": slots})
    
    @action(detail=True, methods=['post'], permission_classes=[IsDoctor])
    def approve(self, request, pk=None):
        appointment = self.get_object()
        appointment.status = 'APPROVED'
        appointment.save()
        return Response({'status': 'approved'})

    @action(detail=True, methods=['post'], permission_classes=[IsPatient])
    def cancel(self, request, pk=None):
        appointment = self.get_object()
        appointment.status = 'CANCELLED'
        appointment.save()
        return Response({'status': 'cancelled'})