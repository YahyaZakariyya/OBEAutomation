from rest_framework import serializers
from programs.models import Program


class ProgramSerializer(serializers.ModelSerializer):
    program_incharge_name = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Program
        fields = ['id', 'program_title', 'program_abbreviation', 'program_incharge', 'program_incharge_name', 'program_type']

    def get_program_incharge_name(self, obj):
        if obj.program_incharge:
            return f"{obj.program_incharge.first_name} {obj.program_incharge.last_name}"
        return None
