import string
from django.db import models
from scheduler.models import LectureSlot, TutorialSlot, LabSlot


class Course(models.Model):
    """
        Represents A Course, which is composed of one or many sections.

    """
    number = models.CharField(max_length=10)  # represented as ID in domain model
    title = models.CharField(max_length=255)  # represented as Name in domain model
    credits = models.DecimalField(max_digits=2, decimal_places=1)  # example: 3.5
    prereqs = models.ManyToManyField("self", symmetrical=False)


class Section(models.Model):
    """

    """
    course = models.ForeignKey(Course)
    lecture = models.ForeignKey(LectureSlot)
    tutorial = models.ForeignKey(TutorialSlot, null=True, blank=True)
    lab = models.ForeignKey(LabSlot, null=True, blank=True)

    @property
    def __unicode__(self):
        # TODO Check if fails if tutorial == NULL or lab == NULL
        return string.join([self.lecture.section_code, self.tutorial.section_code, self.lab.section_code])


class Program(models.Model):
    """
    A program can have one of many offered sequences.
    """
    name = models.CharField(max_length=255)


class Option(models.Model):
    """
    An option carries a course sequence.
    """
    name = models.CharField(max_length=255)
    program = models.ForeignKey(Program)