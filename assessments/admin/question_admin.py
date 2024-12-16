from django.contrib import admin
from sections.models import Section
from outcomes.models import CourseLearningOutcome
from assessments.models import Question
from guardian.shortcuts import get_objects_for_user
from django.forms.models import BaseInlineFormSet
from guardian.admin import GuardedModelAdmin
from django.utils.html import format_html
from django.urls import reverse

class QuestionInlineFormSet(BaseInlineFormSet):
    def __init__(self, *args, **kwargs):
        super(QuestionInlineFormSet, self).__init__(*args, **kwargs)
        # Get the parent Assessment instance
        assessment = self.instance
        section = None
        course = None

        if assessment and assessment.pk:
            # Editing an existing Assessment
            section = assessment.section
            course = section.course
        else:
            # Adding a new Assessment, get section from the form data
            data = kwargs.get('data', None)
            if data:
                # The field name may vary; adjust 'section' accordingly
                section_id = data.get('section')
                if section_id:
                    try:
                        section = Section.objects.get(pk=section_id)
                        course = section.course
                    except Section.DoesNotExist:
                        pass

        # Filter the CLO queryset for each form in the formset
        for form in self.forms:
            clo_field = form.fields.get('clo')
            if clo_field and course:
                clo_field.queryset = CourseLearningOutcome.objects.filter(course=course)
            else:
                clo_field.queryset = CourseLearningOutcome.objects.none()


class QuestionInline(admin.TabularInline):
    model = Question
    formset = QuestionInlineFormSet

    extra = 1
    fields = ['marks', 'clo', 'permission_link']
    readonly_fields = ['permission_link']  # Make the permission_link field read-only
    verbose_name = "Question"
    verbose_name_plural = "Questions"

    def permission_link(self, instance):
        if instance.pk:
            url = reverse('admin:assessments_question_change', args=[instance.pk])
            return format_html('<a href="{}" target="_blank">Manage Permissions</a>', url)
        else:
            return 'Save and continue editing to manage permissions.'

    permission_link.short_description = 'Permissions'  # Set column header
    
    def get_queryset(self, request):
        """
        Customize queryset based on object-level permissions.
        """
        queryset = super().get_queryset(request)
        if request.user.is_superuser:
            return queryset
        return queryset.filter(assessment__section__in=get_objects_for_user(
            request.user, 'sections.view_section', klass=Section
        ))
    
    def has_view_permission(self, request, obj=None):
        return True
    
    def has_add_permission(self, request, obj=None):
        return request.user.has_perm('assessments.can_add_question', obj)

    def has_change_permission(self, request, obj=None):
        return request.user.has_perm('assessments.change_assessment', obj)

    def has_delete_permission(self, request, obj=None):
        return request.user.has_perm('assessments.delete_assessment', obj)

    
class QuestionAdmin(GuardedModelAdmin):
    # Hide the Question model from the admin index page
    def has_module_permission(self, request):
        return False  # This hides the model from the admin index
    
    def has_delete_permission(self, request, obj=None):
        """
        Allow deletion of questions when cascading from an assessment.
        """
        if obj and hasattr(obj, 'assessment'):
            return request.user.has_perm('assessments.delete_assessment', obj.assessment)
        return True

admin.site.register(Question, QuestionAdmin)