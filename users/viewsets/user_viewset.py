from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from users.models import CustomUser
from users.serializers import (
    CustomUserSerializer,
    CustomUserDetailSerializer,
    CustomUserCreateSerializer
)


class UserViewSet(viewsets.ModelViewSet):
    """
    ViewSet for CustomUser model
    Provides CRUD operations for Users
    """
    queryset = CustomUser.objects.all()
    permission_classes = [permissions.IsAuthenticated]

    def get_serializer_class(self):
        if self.action == 'create':
            return CustomUserCreateSerializer
        elif self.action == 'retrieve':
            return CustomUserDetailSerializer
        return CustomUserSerializer

    def get_queryset(self):
        queryset = CustomUser.objects.all()
        user = self.request.user

        # Filter by role if provided
        role = self.request.query_params.get('role', None)
        if role:
            queryset = queryset.filter(role=role)

        # Non-admin users can only see themselves unless they're faculty
        if user.role == 'student':
            queryset = queryset.filter(id=user.id)
        elif user.role == 'faculty':
            # Faculty can see students in their sections
            view_all = self.request.query_params.get('view_all', 'false')
            if view_all.lower() != 'true':
                from django.db.models import Q
                # Get students from sections taught by this faculty
                section_students = CustomUser.objects.filter(
                    enrolled_sections__faculty=user
                ).distinct()
                queryset = queryset.filter(
                    Q(id=user.id) | Q(id__in=section_students)
                )

        return queryset.order_by('username')

    @action(detail=True, methods=['get'])
    def sections(self, request, pk=None):
        """Get sections for a user (enrolled for students, taught for faculty)"""
        user = self.get_object()
        from sections.serializers import SectionSerializer

        if user.role == 'student':
            sections = user.enrolled_sections.all()
        elif user.role == 'faculty':
            sections = user.taught_sections.all()
        else:
            sections = []

        serializer = SectionSerializer(sections, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def me(self, request):
        """Get current user's profile"""
        serializer = CustomUserDetailSerializer(request.user)
        return Response(serializer.data)
