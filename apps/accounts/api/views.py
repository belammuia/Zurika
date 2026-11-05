from rest_framework import generics
from rest_framework.permissions import IsAdminUser, IsAuthenticated
from rest_framework.views import APIView
from rest_framework.response import Response
from .serializers import CustomRegistrationSerializer, CustomUserProfileSerializer
from django.contrib.auth import get_user_model
from ..models import Profile
from apps.core.permissions import IsAdmin


User = get_user_model()

class CustomRegistrationView(generics.CreateAPIView):
    permission_classes = [IsAdmin]
    serializer_class = CustomRegistrationSerializer

class CustomGetCurrentUserView(generics.RetrieveAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = CustomUserProfileSerializer

    def get_object(self):
        return Profile.objects.select_related("user").get(
            user=self.request.user
        )


        


