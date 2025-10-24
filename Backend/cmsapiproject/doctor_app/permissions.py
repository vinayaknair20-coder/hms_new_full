from rest_framework import permissions


class IsDoctor(permissions.BasePermission):
    """
    Custom permission to only allow doctors to access views.
    """
    def has_permission(self, request, view):
        # Check if user is authenticated
        if not request.user.is_authenticated:
            return False
        
        # Allow admin users full access
        if request.user.is_staff or request.user.is_superuser:
            return True
        
        # Check if user is a doctor (based on role field)
        return hasattr(request.user, 'role') and request.user.role in ['Doctor']
    
    def has_object_permission(self, request, view, obj):
        # Admin users have full access
        if request.user.is_staff or request.user.is_superuser:
            return True
            
        # Check if the object belongs to the logged-in doctor
        if hasattr(obj, 'doctor'):
            return obj.doctor.user == request.user

        return False
