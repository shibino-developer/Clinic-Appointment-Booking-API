from django.contrib import admin
from django.urls import path, include
from rest_framework.routers import DefaultRouter

from appointments.views import AppointmentViewSet
from doctors.views import DoctorViewSet
from accounts.views import RegisterView
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView


router = DefaultRouter()
router.register('appointments', AppointmentViewSet, basename='appointments')
router.register('doctors', DoctorViewSet, basename='doctors')


urlpatterns = [
    path('admin/', admin.site.urls),

    path('api/register/', RegisterView.as_view()),
    path('api/login/', TokenObtainPairView.as_view()),
    path('api/token/refresh/', TokenRefreshView.as_view()),

    path('api-auth/', include('rest_framework.urls')),
    path('api/', include(router.urls)),

    path('api/appointments/<int:pk>/cancel/',
         AppointmentViewSet.as_view({'post': 'cancel'})),

    path('api/appointments/<int:pk>/approve/',
         AppointmentViewSet.as_view({'post': 'approve'})),
]