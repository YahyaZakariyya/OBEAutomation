from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404
from .models import Assessment, Question, StudentQuestionScore
from .serializers import QuestionSerializer, StudentSerializer, StudentQuestionScoreSerializer

class AssessmentDataAPI(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        assessment_id = request.query_params.get('id')
        assessment = get_object_or_404(Assessment, id=assessment_id)

        # Get questions
        questions = Question.objects.filter(assessment=assessment)
        question_data = QuestionSerializer(questions, many=True).data

        # Get students enrolled in that assessment’s section
        students = assessment.section.students.all()
        student_data = StudentSerializer(students, many=True).data

        # Get scores
        scores = StudentQuestionScore.objects.filter(question__assessment=assessment)
        score_data = StudentQuestionScoreSerializer(scores, many=True).data

        return Response({
            'questions': question_data,
            'students': student_data,
            'scores': score_data
        })

class UpdateScoresAPI(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        # Expecting data in the form:
        # { "scores": [{ "student_id": x, "question_id": y, "score": z }, ...] }
        data = request.data.get('marks_obtained', [])
        for score_item in data:
            student_id = score_item['student_id']
            question_id = score_item['question_id']
            new_score = score_item['marks_obtained']

            # Update the marks_obtained in the DB
            StudentQuestionScore.objects.filter(student_id=student_id, question_id=question_id).update(marks_obtained=new_score)

        return Response({"status": "success"})

import os
from django.conf import settings
from django.http import HttpResponse
from django.views import View

class ReactAppView(View):
    def get(self, request, *args, **kwargs):
        # Construct the path to your index.html file
        index_file = os.path.join(
            settings.BASE_DIR,
            'frontend',  # folder name where your React app is
            'build',     # the build output folder
            'index.html'
        )
        
        # Check if index.html exists
        if not os.path.exists(index_file):
            return HttpResponse("Build not found. Did you run npm run build?", status=501)
        
        with open(index_file, 'r', encoding='utf-8') as file:
            html_content = file.read()
        return HttpResponse(html_content)
