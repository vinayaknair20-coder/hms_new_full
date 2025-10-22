from django.shortcuts import render
from rest_framework import viewsets
from .models import User, Specialization, Staff, Doctor
from .serializers import UserSerializer, SpecializationSerializer, StaffSerializer, DoctorSerializer
from common.permissions import IsDoctor, IsPharmacist, IsAdmin, IsReceptionist 
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import api_view, permission_classes


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAdmin]


class SpecializationViewSet(viewsets.ModelViewSet):
    queryset = Specialization.objects.all()
    serializer_class = SpecializationSerializer
    permission_classes = [IsAdmin]


class StaffViewSet(viewsets.ModelViewSet):
    queryset = Staff.objects.all()
    serializer_class = StaffSerializer
    permission_classes = [IsAdmin]


class DoctorViewSet(viewsets.ModelViewSet):
    queryset = Doctor.objects.all()
    serializer_class = DoctorSerializer
    permission_classes = [IsAdmin]


class MeView(APIView):
    """Return current authenticated user info."""
    permission_classes = [IsAuthenticated]

    def get(self, request):
        serializer = UserSerializer(request.user)
        return Response(serializer.data)


class CreateUserWithProfiles(APIView):
    """Create a User and optional Staff/Doctor records atomically."""
    permission_classes = [IsAuthenticated, IsAdmin]

    def post(self, request):
        from .serializers import UserWithProfilesSerializer

        # Defensive: clean empty or null nested objects that may be sent by the client
        # request.data can be a QueryDict or regular dict - normalize to a shallow dict
        try:
            payload = request.data.copy()
        except Exception:
            # fallback: coerce to dict
            payload = dict(request.data)

        # remove doctor/staff if they are null/empty/'null' string or an empty dict/list
        for key in ('staff', 'doctor'):
            if key in payload:
                val = payload.get(key)
                # handle JSON null / Python None
                if val is None:
                    payload.pop(key, None)
                    continue
                # handle string representations like 'null' or empty string
                if isinstance(val, str) and val.strip().lower() in ('', 'null', 'none'):
                    payload.pop(key, None)
                    continue
                # handle QueryDict/list coming from form-data where value may be list or dict
                if isinstance(val, (list, tuple)) and len(val) == 0:
                    payload.pop(key, None)
                    continue
                if isinstance(val, dict):
                    # if all values are blank/null, remove the key
                    if all(v in (None, '') for v in val.values()):
                        payload.pop(key, None)

        serializer = UserWithProfilesSerializer(data=payload)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        return Response({"id": user.id, "username": user.username}, status=201)


# ========================
# ✅ NEW FUNCTION - USER PROFILE FOR LOGIN
# ========================
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_user_profile(request):
    """
    Get current user's profile with role
    Used by frontend Login to determine which dashboard to route to
    Endpoint: GET /api/users/profile/
    """
    user = request.user
    
    return Response({
        'username': user.username,
        'email': user.email,
        'first_name': user.first_name,
        'last_name': user.last_name,
        'role': user.role,  # Critical: Returns actual role from database
        'is_active': user.is_active,
    })
