from django.contrib import admin
from obesystem.models import Question, CourseLearningOutcome
from django import forms

class QuestionForm(forms.ModelForm):
    class Meta:
        model = Question
        fields = "__all__"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance and self.instance.assessment_id:
            course = self.instance.assessment.section.course  # Get the course from the related section
            print(course)
            self.fields["clo"].queryset = CourseLearningOutcome.objects.filter(course=course)
            print(self.fields["clo"].queryset)
        else:
            self.fields["clo"].queryset = CourseLearningOutcome.objects.none()


class QuestionInline(admin.TabularInline):
    model = Question
    form = QuestionForm
    extra = 1  # Number of blank forms displayed for adding questions
    # readonly_fields = ['number']
    fields = ['number', 'marks', 'clo'] 
    verbose_name = "Question"
    verbose_name_plural = "Questions"
    
    class Media:
        js = ("admin/js/question_admin.js",)  # Include the JavaScript file

class QuestionAdmin(admin.ModelAdmin):
    # readonly_fields = ['number']  # Makes the question number visible but not editable
    list_display = ('assessment', 'number', 'marks')
    list_filter = ('assessment',)

admin.site.register(Question, QuestionAdmin)