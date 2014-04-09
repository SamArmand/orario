import string
from django.db import models
from sortedm2m.fields import SortedManyToManyField
from scheduler.models import LectureSlot, TutorialSlot, LabSlot


class Course(models.Model):
    """
    Represents A Course, which is composed of one or many sections.
    """
    #: Course number, e.g. "SOEN 331."
    number = models.CharField(max_length=10)
    #: A short description of the course.
    title = models.CharField(max_length=255)
    #: The number of credits the course is worth.
    credits = models.DecimalField(max_digits=2, decimal_places=1)
    #: The prerequisite courses for this course.
    prereqs = models.ManyToManyField("self", symmetrical=False, related_name='prereq_by')
    #: The corequisite courses for this course.
    coreqs = models.ManyToManyField("self", symmetrical=False, related_name='coreq_by')

    def __unicode__(self):
        """Returns string representation of the course."""
        return "%s - %s" % (self.number, self.title)

    def is_coreq_for(self, course):
        """
        Returns whether this course is a corequisite for the specified
        course.
        """
        return self in course.coreqs.all()


class Section(models.Model):
    """
    Describes a course section that is a unique combination of a lecture,
    an optional tutorial, and an optional lab.
    """
    #: The course this section belongs to.
    course = models.ForeignKey(Course)
    #: The term the section belongs to.
    term = models.IntegerField()
    #: The lecture in this section.
    lecture = models.ForeignKey(LectureSlot)
    #: The tutorial in this section. Optional.
    tutorial = models.ForeignKey(TutorialSlot, null=True, blank=True)
    #: The lab in this section. Optional.
    lab = models.ForeignKey(LabSlot, null=True, blank=True)

    def __unicode__(self):
        """
        Returns the complete section code, e.g. AA AJ AL
        """
        return string.join([
            self.course.__unicode__(),
            self.lecture.section_code,
            self.tutorial.section_code if self.tutorial is not None else '',
            self.lab.section_code if self.lab is not None else ''])

    def conflicts_with(self, other):
        """
        Returns true if the section has a time conflict with the specified
        Section or TimeSlot, and false otherwise.
        """
        from scheduler.models import TimeSlot
        assert isinstance(other, TimeSlot) or isinstance(other, Section)
        if isinstance(other, TimeSlot):
            return (
                other.conflicts_with(self.lecture) or
                other.conflicts_with(self.tutorial) or
                other.conflicts_with(self.lab)
            )
        elif isinstance(other, Section):
            lect_conflict = (
                other.lecture.conflicts_with(self.lecture) or
                other.lecture.conflicts_with(self.tutorial) or
                other.lecture.conflicts_with(self.lab)
            )
            if other.tutorial is not None:
                tut_conflict = (
                    other.tutorial.conflicts_with(self.lecture) or
                    other.tutorial.conflicts_with(self.tutorial) or
                    other.tutorial.conflicts_with(self.lab)
                )
            else:
                tut_conflict = False
            if other.lab is not None:
                lab_conflict = (
                    other.lab.conflicts_with(self.lecture) or
                    other.lab.conflicts_with(self.tutorial) or
                    other.lab.conflicts_with(self.lab)
                )
            else:
                lab_conflict = False
            return (
                lect_conflict or
                tut_conflict or
                lab_conflict
            )


class Program(models.Model):
    """
    A program can have one of many offered sequences.
    """
    #: Name of the program.
    name = models.CharField(max_length=255)

    def __unicode__(self):
        return self.name

class Option(models.Model):
    """
    An option carries a course sequence.
    """
    #: Name of the option.
    name = models.CharField(max_length=255)
    #: Program that the Option belongs to.
    program = models.ForeignKey(Program)
    #: The courses listed in suggested order of completion.
    sequence = SortedManyToManyField(Course)

    def __unicode__(self):
        return self.name