from django.contrib import admin
from django.urls import path, include
from rest_framework.routers import DefaultRouter

from appointments.views import AppointmentViewSet
from doctors.views import DoctorViewSet
from accounts.views import RegisterView
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from django.urls import re_path

router = DefaultRouter()
router.register(r'appointments', AppointmentViewSet, basename='appointment')
router.register(r'doctors', DoctorViewSet, basename='doctor')

schema_view = get_schema_view(
    openapi.Info(
        title="Clinic API",
        default_version='v1',
        description="Doctor Appointment Booking API",
    ),
    public=True,
    permission_classes=(permissions.AllowAny,),
)
urlpatterns = [
    path('admin/', admin.site.urls),

    path('api/register/', RegisterView.as_view()),
    path('api/login/', TokenObtainPairView.as_view()),
    path('api/token/refresh/', TokenRefreshView.as_view()),

    path('api-auth/', include('rest_framework.urls')),
    path('api/', include(router.urls)),
    re_path(r'^swagger/$', schema_view.with_ui('swagger', cache_timeout=0)),
    re_path(r'^redoc/$', schema_view.with_ui('redoc', cache_timeout=0)),
]
