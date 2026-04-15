from rest_framework import viewsets
from .models import Doctor
from .serializers import DoctorSerializer


class DoctorViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Doctor.objects.all()
    serializer_class = DoctorSerializer