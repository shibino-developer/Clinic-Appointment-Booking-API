"""
URL configuration for config project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/6.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from django.http import HttpResponse
from appointments.views import AppointmentViewSet
from accounts.views import RegisterView
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView


router = DefaultRouter()
router.register(r'appointments', AppointmentViewSet, basename='appointments')


urlpatterns = [
    path('admin/', admin.site.urls),

    # 🔐 Auth APIs
    path('api/register/', RegisterView.as_view(), name='register'),
    path('api/login/', TokenObtainPairView.as_view(), name='login'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('api-auth/', include('rest_framework.urls')),

    # 📅 Appointment APIs
    path('api/', include(router.urls)),

    # Custom actions (manual endpoints)
    path('api/appointments/<int:pk>/cancel/', 
         AppointmentViewSet.as_view({'post': 'cancel'})),

    path('api/appointments/<int:pk>/reschedule/', 
         AppointmentViewSet.as_view({'post': 'reschedule'})),

    path('api/appointments/<int:pk>/approve/', 
         AppointmentViewSet.as_view({'post': 'approve'})),
]
def profile(request):
    return HttpResponse("Logged in successfully")

urlpatterns += [
    path('accounts/profile/', profile),
]