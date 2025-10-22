from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework_simplejwt.views import TokenObtainPairView

class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    """Custom JWT serializer that includes user role and additional info"""
    
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        
        # Add custom claims to JWT token
        token['role'] = user.role
        token['username'] = user.username
        token['email'] = user.email if user.email else ''
        
        return token
    
    def validate(self, attrs):
        data = super().validate(attrs)
        
        # Add extra responses (sent in API response, not in token)
        data['user'] = {
            'id': self.user.id,
            'username': self.user.username,
            'email': self.user.email,
            'role': self.user.role,
            'first_name': self.user.first_name,
            'last_name': self.user.last_name,
        }
        
        return data

class CustomTokenObtainPairView(TokenObtainPairView):
    """Custom view for obtaining JWT tokens"""
    serializer_class = CustomTokenObtainPairSerializer
