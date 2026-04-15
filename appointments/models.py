from django.db import models
from django.conf import settings
from doctors.models import Doctor


class Appointment(models.Model):
    STATUS_CHOICES = (
        ('PENDING', 'Pending'),
        ('APPROVED', 'Approved'),
        ('CANCELLED', 'Cancelled'),
        ('RESCHEDULED', 'Rescheduled'),
    )

    patient = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='patient_appointments'
    )
    doctor = models.ForeignKey(
        Doctor,
        on_delete=models.CASCADE,
        related_name='doctor_appointments'
    )

    date = models.DateField()
    time = models.TimeField()

    status = models.CharField(
        max_length=15,
        choices=STATUS_CHOICES,
        default='PENDING'
    )

    reason = models.TextField(blank=True, null=True)

    prescription = models.FileField(
        upload_to='prescriptions/',
        blank=True,
        null=True
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ['doctor', 'date', 'time']  # prevents double booking
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.patient} → {self.doctor} ({self.date} {self.time})"