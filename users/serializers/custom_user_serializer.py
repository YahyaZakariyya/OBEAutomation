from rest_framework import serializers
from users.models import CustomUser


class CustomUserSerializer(serializers.ModelSerializer):
    """Basic User serializer"""
    full_name = serializers.SerializerMethodField()

    class Meta:
        model = CustomUser
        fields = ['id', 'username', 'first_name', 'last_name', 'email', 'role', 'full_name']
        read_only_fields = ['id']

    def get_full_name(self, obj):
        return obj.get_full_name()


class CustomUserDetailSerializer(serializers.ModelSerializer):
    """Detailed User serializer with relationships"""
    full_name = serializers.SerializerMethodField()
    enrolled_sections_count = serializers.SerializerMethodField()
    taught_sections_count = serializers.SerializerMethodField()

    class Meta:
        model = CustomUser
        fields = [
            'id',
            'username',
            'first_name',
            'last_name',
            'email',
            'role',
            'full_name',
            'enrolled_sections_count',
            'taught_sections_count',
        ]
        read_only_fields = ['id']

    def get_full_name(self, obj):
        return obj.get_full_name()

    def get_enrolled_sections_count(self, obj):
        if obj.role == 'student':
            return obj.enrolled_sections.count()
        return 0

    def get_taught_sections_count(self, obj):
        if obj.role == 'faculty':
            return obj.taught_sections.count()
        return 0


class CustomUserCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating users"""
    password = serializers.CharField(write_only=True, required=True, style={'input_type': 'password'})

    class Meta:
        model = CustomUser
        fields = ['username', 'first_name', 'last_name', 'email', 'role', 'password']

    def create(self, validated_data):
        user = CustomUser.objects.create_user(**validated_data)
        return user