from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from sections.models import Section
from assessments.models import AssessmentBreakdown

@receiver(post_save, sender=Section)
def create_assessmentbreakdown(sender, instance, created, **kwargs):
    """
    Automatically create an AssessmentBreakdown when a Section is created.
    Initialize all weightage to 0 except for `final_weightage` which is set to 100%.
    """
    if created:
        AssessmentBreakdown.objects.create(
            section=instance,
            assignment_weightage=0,
            quiz_weightage=0,
            lab_weightage=0,
            mid_weightage=0,
            final_weightage=100,  # Set 100% weightage for Finals
            project_weightage=0,
        )

@receiver(post_delete, sender=Section)
def delete_assessmentbreakdowns_on_section_delete(sender, instance, **kwargs):
    """
    Automatically delete related AssessmentBreakdown objects when a Section is deleted.
    """
    # Fetch all related AssessmentBreakdown objects
    assessment_breakdowns = AssessmentBreakdown.objects.filter(section=instance)
    
    # Delete related AssessmentBreakdown objects
    assessment_breakdowns.delete()