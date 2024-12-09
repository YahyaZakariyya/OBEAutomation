from django.test import TestCase
from obesystem.models import Question, StudentQuestionScore, CustomUser, Assessment, Section

class QuestionSignalTest(TestCase):
    def setUp(self):
        # Create a section with students
        self.section = Section.objects.create(name="Test Section")
        self.student1 = CustomUser.objects.create(username="student1")
        self.student2 = CustomUser.objects.create(username="student2")
        self.section.students.add(self.student1, self.student2)

        # Create an assessment
        self.assessment = Assessment.objects.create(title="Test Assessment", section=self.section)

    def test_scores_created_on_question_creation(self):
        # Test automatic creation of scores when a question is created
        question = Question.objects.create(assessment=self.assessment, marks=10.0)
        scores = StudentQuestionScore.objects.filter(question=question)
        self.assertEqual(scores.count(), 2)  # Two students, so two entries should exist
        self.assertEqual(scores.first().marks_obtained, 0.0)  # Default value should be 0.0

    def test_scores_deleted_on_question_deletion(self):
        # Test automatic deletion of scores when a question is deleted
        question = Question.objects.create(assessment=self.assessment, marks=10.0)
        self.assertEqual(StudentQuestionScore.objects.filter(question=question).count(), 2)
        question.delete()
        self.assertEqual(StudentQuestionScore.objects.filter(question=question).count(), 0)  # All entries should be deleted
