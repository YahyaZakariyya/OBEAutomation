from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from users.models import CustomUser
from users.serializers import CustomUserSerializer
from api.permissions import IsAdminUser

class UserListCreateAPI(generics.ListCreateAPIView):
    permission_classes = [IsAuthenticated, IsAdminUser]
    queryset = CustomUser.objects.all()
    serializer_class = CustomUserSerializer

class UserDetailAPI(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [IsAuthenticated, IsAdminUser]
    queryset = CustomUser.objects.all()
    serializer_class = CustomUserSerializer
