from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import UserViewSet, SpecializationViewSet, StaffViewSet, DoctorViewSet, MeView, CreateUserWithProfiles, get_user_profile  # ← ADD get_user_profile

router = DefaultRouter()
router.register(r'users', UserViewSet)
router.register(r'specializations', SpecializationViewSet)
router.register(r'staffs', StaffViewSet)
router.register(r'doctors', DoctorViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('me/', MeView.as_view(), name='me'),
    path('users-with-profiles/', CreateUserWithProfiles.as_view(), name='users-with-profiles'),
    path('profile/', get_user_profile, name='user-profile'),  # ← ADD THIS LINE
]
