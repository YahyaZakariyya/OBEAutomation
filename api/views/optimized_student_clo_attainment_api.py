import pandas as pd
import numpy as np
from decimal import Decimal
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from assessments.models import Question, StudentQuestionScore
from sections.models import Section
from outcomes.models import CourseLearningOutcome
from django.shortcuts import get_object_or_404


class OptimizedStudentCLOAttainment(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, section_id, student_id):
        """
        Optimized API using Pandas and NumPy for fast processing of detailed Student OBE result.
        """

        # Get Section
        section = get_object_or_404(Section, id=section_id)

        # Get all CLOs for the Course
        clos = CourseLearningOutcome.objects.filter(course=section.course)

        # CLO Data Structure
        clo_data = {
            clo.id: {
                "cloCode": f"CLO{clo.CLO}",
                "title": clo.heading,
                "weightage": clo.weightage,
                "totalMarks": 0,
                "studentScore": 0,
                "questions": []
            }
            for clo in clos
        }

        # Load all relevant data into Pandas DataFrames
        student_scores = StudentQuestionScore.objects.filter(
            student_id=student_id, 
            question__assessment__section=section
        ).select_related('question', 'question__assessment')

        # Convert ORM QuerySet to Pandas DataFrame
        data = pd.DataFrame(list(student_scores.values(
            'question_id', 
            'marks_obtained', 
            'question__marks', 
            'question__assessment__type'
        )))

        # Rename Columns for Easier Handling
        data.rename(columns={
            'question_id': 'QuestionID',
            'marks_obtained': 'ObtainedMarks',
            'question__marks': 'TotalMarks',
            'question__assessment__type': 'AssessmentType'
        }, inplace=True)

        # ✅ Convert Decimal to Float Before Computation
        data['ObtainedMarks'] = data['ObtainedMarks'].astype(float)
        data['TotalMarks'] = data['TotalMarks'].astype(float)

        # Compute Normalized Scores
        data['ScorePercentage'] = (data['ObtainedMarks'] / data['TotalMarks']) * 100

        # Fetch CLO mappings
        question_clo_mappings = {}
        for question in Question.objects.filter(assessment__section=section):
            question_clo_mappings[question.id] = list(question.clo.values_list('id', flat=True))

        # Expand CLO Mapping into DataFrame
        expanded_rows = []
        for _, row in data.iterrows():
            question_id = row['QuestionID']
            if question_id in question_clo_mappings:
                for clo_id in question_clo_mappings[question_id]:
                    expanded_rows.append({**row.to_dict(), "CLO_ID": clo_id})

        expanded_data = pd.DataFrame(expanded_rows)

        # Aggregate Student Attainment for Each CLO
        student_clo_scores = expanded_data.groupby("CLO_ID").agg({
            'ScorePercentage': 'mean'
        }).reset_index()

        # Include Detailed Breakdown Per Question
        detailed_questions = []
        for _, row in expanded_data.iterrows():
            detailed_questions.append({
                "questionId": row["QuestionID"],
                "assessmentType": row["AssessmentType"],
                "totalMarks": row["TotalMarks"],
                "obtainedMarks": row["ObtainedMarks"],
                "normalizedScore": round(row["ScorePercentage"], 2),
                "CLO_ID": row["CLO_ID"]
            })

        # Convert Results to JSON Response
        response_data = {
            "status": "success",
            "message": "Student OBE result fetched successfully.",
            "data": {
                "studentId": student_id,
                "sectionId": section.id,
                "CLOs": student_clo_scores.to_dict(orient="records"),
                "detailedQuestions": detailed_questions  # Added full breakdown of each question
            }
        }

        return Response(response_data)
