from django.contrib import admin
from django.urls import path, include
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)


urlpatterns = [
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),     # login (get access/refresh token)
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),    
    path('admin/', admin.site.urls),
    path('api/admin/', include('admin_app.urls')),
    path('api/receptionist/', include('receptionist_app.urls')),
    path('api/doctor/', include('doctor_app.urls')),
    path('api/pharmacist/', include('pharmacist_app.urls')),
    path('api/lab_technician/', include('lab_technician_app.urls')),
]
