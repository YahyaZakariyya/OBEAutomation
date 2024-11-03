from django.contrib import admin
from django.forms import BaseInlineFormSet, ValidationError
from obesystem.models import Question

# Custom inline formset to enforce the total marks constraint
class QuestionInlineFormSet(BaseInlineFormSet):
    def clean(self):
        super().clean()
        total_marks = 0
        for form in self.forms:
            if form.cleaned_data and not form.cleaned_data.get('DELETE', False):
                total_marks += form.cleaned_data['marks']

        # Check if total marks exceed the assessment's total marks
        if total_marks > self.instance.marks:
            raise ValidationError(f"Total marks for questions ({total_marks}) exceed the available assessment marks ({self.instance.marks}).")

class QuestionInline(admin.TabularInline):
    model = Question
    formset = QuestionInlineFormSet
    extra = 1
    fields = ['text', 'marks', 'clo']

    def save_model(self, request, obj, form, change):
        # Save the object first to get the ID
        super().save_model(request, obj, form, change)
        # Handle Many-to-Many fields after the object has an ID
        form.save_m2m()

    # Prevent questions from being added until the assessment is created
    def has_add_permission(self, request, obj):
        if obj is None:
            return False  # No adding questions before an assessment is created
        return super().has_add_permission(request, obj)
    
class QuestionAdmin(admin.ModelAdmin):
    list_display = ('assessment', 'text', 'marks')
    list_filter = ('assessment',)
    search_fields = ('text',)

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs
        return qs.filter(assessment__section__faculty=request.user)

    def has_module_permission(self, request):
        """Restrict direct visibility of Questions to superusers."""
        return request.user.is_superuser
    
# admin.site.register(Question, QuestionAdmin)