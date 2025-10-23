from django.contrib import admin
from django.urls import path, include
from rest_framework_simplejwt.views import TokenRefreshView
from common.serializers import CustomTokenObtainPairView  # ✅ Import custom view
from admin_app.views import login_view  # ✅ Import login view (if you have it)


urlpatterns = [
    # JWT Token endpoints
    path('api/token/', CustomTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    
    # ✅ LOGIN ENDPOINT (if login_view exists in admin_app)
    path('api/auth/login/', login_view, name='login'),
    
    # Django Admin Panel
    path('admin/', admin.site.urls),
    
    # ✅ FIXED - Changed from 'api/users/' to 'api/admin/'
    path('api/admin/', include('admin_app.urls')),  # ← THIS IS THE FIX!
    
    # Other app endpoints
    path('api/receptionist/', include('receptionist_app.urls')),
    path('api/doctor/', include('doctor_app.urls')),
    path('api/pharmacist/', include('pharmacist_app.urls')),
    path('api/lab_technician/', include('lab_technician_app.urls')),
]
