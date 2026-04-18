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
    doctor = models.ForeignKey(Doctor, on_delete=models.CASCADE)
    date = models.DateField()
    time = models.TimeField()
    status = models.CharField(max_length=15, choices=STATUS_CHOICES, default='PENDING')
    reason = models.TextField(blank=True, null=True)
    prescription = models.FileField(upload_to='prescriptions/', null=True, blank=True)

    class Meta:
        unique_together = ['doctor', 'date', 'time']

    def __str__(self):
        return f"{self.patient} - {self.doctor}"
    

class Notification(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    message = models.TextField()
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.message