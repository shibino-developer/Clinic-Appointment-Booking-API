from django.contrib import admin
from django.urls import path, include
from rest_framework.routers import DefaultRouter

from appointments.views import AppointmentViewSet
from doctors.views import DoctorViewSet
from accounts.views import RegisterView
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

router = DefaultRouter()
router.register(r'appointments', AppointmentViewSet, basename='appointment')
router.register(r'doctors', DoctorViewSet, basename='doctor')

urlpatterns = [
    path('admin/', admin.site.urls),

    path('api/register/', RegisterView.as_view()),
    path('api/login/', TokenObtainPairView.as_view()),
    path('api/token/refresh/', TokenRefreshView.as_view()),

    path('api-auth/', include('rest_framework.urls')),
    path('api/', include(router.urls)),
]