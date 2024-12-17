from rest_framework import serializers
from sections.models import Section

class SectionSerializer(serializers.ModelSerializer):
    course_id = serializers.IntegerField(source='course.id', read_only=True)

    class Meta:
        model = Section
        fields = ['id', 'course_id']  # Expose Section ID and Course ID
