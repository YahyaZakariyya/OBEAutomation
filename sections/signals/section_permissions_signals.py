from django.db.models.signals import post_delete, m2m_changed, post_save, pre_save
from django.dispatch import receiver
from sections.models import Section
from assessments.models import AssessmentBreakdown, Question, StudentQuestionScore
from users.models import CustomUser
from guardian.shortcuts import assign_perm
from django.contrib.auth.models import Group

@receiver(pre_save, sender=Section)
def track_old_faculty(sender, instance, **kwargs):
    """
    Tracks the old faculty before the section is saved.
    """
    if instance.pk:  # Only if the instance already exists
        old_faculty = Section.objects.filter(pk=instance.pk).first().faculty
        instance._old_faculty = old_faculty  # Store the old faculty in a temporary attribute

@receiver(post_save, sender=Section)
def handle_section_creation_or_update(sender, instance, created, **kwargs):
    """
    Handles permissions when a Section is created or updated.
    """
    faculty_group_name = f"faculty_section_{instance.pk}"
    students_group_name = f"students_section_{instance.pk}"

    # Get or create the groups
    faculty_group, _ = Group.objects.get_or_create(name=faculty_group_name)
    students_group, _ = Group.objects.get_or_create(name=students_group_name)

    if created:
        # Assign permissions for faculty group
        assign_perm('sections.view_section', faculty_group, instance)
        assign_perm('sections.can_add_assessment', faculty_group, instance)

        # Assign permissions for students group
        assign_perm('sections.view_section', students_group, instance)

        assessment_breakdowns = AssessmentBreakdown.objects.filter(section=instance)
        for breakdown in assessment_breakdowns:
            assign_perm('assessments.view_assessmentbreakdown', faculty_group, breakdown)
            assign_perm('assessments.change_assessmentbreakdown', faculty_group, breakdown)
            assign_perm('assessments.view_assessmentbreakdown', students_group, breakdown)

        # Add faculty and students to their groups
        if instance.faculty:
            instance.faculty.groups.add(faculty_group)
        for student in instance.students.all():
            student.groups.add(students_group)
    else:
        # Handle faculty change
        old_faculty = getattr(instance, '_old_faculty', None)  # Get the old faculty from pre_save
        if old_faculty and old_faculty != instance.faculty:
            if old_faculty:
                old_faculty.groups.remove(faculty_group)  # Remove old faculty from the group
            if instance.faculty:
                instance.faculty.groups.add(faculty_group)


@receiver(m2m_changed, sender=Section.students.through)
def handle_students_membership_change(sender, instance, action, pk_set, **kwargs):
    """
    Updates student permissions when students are added or removed from a Section.
    """
    students_group_name = f"students_section_{instance.pk}"
    students_group = Group.objects.get(name=students_group_name)

    if action == "post_add":
        # Add students to the group
        for student_id in pk_set:
            student = instance.students.get(pk=student_id)
            student.groups.add(students_group)
            # Get all questions related to the section's assessments
            questions = Question.objects.filter(assessment__section=instance)
            for question in questions:
                # Create StudentQuestionScore for the student for each question
                StudentQuestionScore.objects.get_or_create(
                    student=student,
                    question=question,
                    defaults={'marks_obtained': 0}  # Default marks can be set to 0
                )
    elif action == "post_remove":
        # Remove students from the group
        for student_id in pk_set:
            try:
                # Fetch the student directly from the database
                student = CustomUser.objects.get(pk=student_id)
                student.groups.remove(students_group)
                # Get all related StudentQuestionScore entries and delete them
                StudentQuestionScore.objects.filter(
                    student=student,
                    question__assessment__section=instance
                ).delete()
            except CustomUser.DoesNotExist:
                # Log the error if the student does not exist in the database (very unlikely in this case)
                print(f"CustomUser with ID {student_id} does not exist.")


@receiver(post_delete, sender=Section)
def handle_section_deletion(sender, instance, **kwargs):
    """
    Cleans up groups and permissions when a Section is deleted.
    """
    faculty_group_name = f"faculty_section_{instance.pk}"
    students_group_name = f"students_section_{instance.pk}"

    # Delete the groups, which automatically removes all associated permissions
    Group.objects.filter(name=faculty_group_name).delete()
    Group.objects.filter(name=students_group_name).delete()