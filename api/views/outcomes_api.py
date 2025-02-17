from rest_framework.response import Response
from rest_framework.decorators import api_view
from outcomes.models import CourseLearningOutcome, ProgramLearningOutcome
from outcomes.serializers import CLOSerializer, PLOSerializer

@api_view(['GET'])
def get_plos_by_program(request, program_id):
    plos = ProgramLearningOutcome.objects.filter(program_id=program_id)
    serializer = PLOSerializer(plos, many=True)
    return Response(serializer.data)

@api_view(['GET'])
def get_clos_by_course(request, course_id):
    clos = CourseLearningOutcome.objects.filter(course=course_id)
    serializer = CLOSerializer(clos, many=True)
    return Response(serializer.data)