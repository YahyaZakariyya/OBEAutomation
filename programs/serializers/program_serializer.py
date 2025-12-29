from rest_framework import serializers
from programs.models import Program
from users.serializers import CustomUserSerializer


class ProgramSerializer(serializers.ModelSerializer):
    """Detailed Program serializer with nested relationships"""
    program_incharge = CustomUserSerializer(read_only=True)
    program_incharge_id = serializers.PrimaryKeyRelatedField(
        queryset=None,  # Will be set in __init__
        source='program_incharge',
        write_only=True,
        required=False,
        allow_null=True
    )

    class Meta:
        model = Program
        fields = [
            'id',
            'program_title',
            'program_abbreviation',
            'program_type',
            'program_incharge',
            'program_incharge_id',
        ]
        read_only_fields = ['id']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Import here to avoid circular imports
        from users.models import CustomUser
        self.fields['program_incharge_id'].queryset = CustomUser.objects.filter(role='faculty')


class ProgramListSerializer(serializers.ModelSerializer):
    """Lightweight Program serializer for list views"""
    program_incharge_name = serializers.CharField(
        source='program_incharge.get_full_name',
        read_only=True
    )

    class Meta:
        model = Program
        fields = [
            'id',
            'program_title',
            'program_abbreviation',
            'program_type',
            'program_incharge_name',
        ]
