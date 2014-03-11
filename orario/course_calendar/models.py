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
    prereqs = models.ManyToManyField("self", symmetrical=False, related_name='prereq_by')
    coreqs = models.ManyToManyField("self", symmetrical=False, related_name='coreq_by')

    def __unicode__(self):
        return self.number


class Section(models.Model):
    """

    """
    course = models.ForeignKey(Course)
    lecture = models.ForeignKey(LectureSlot)
    tutorial = models.ForeignKey(TutorialSlot, null=True, blank=True)
    lab = models.ForeignKey(LabSlot, null=True, blank=True)

    def __unicode__(self):
        return string.join([
            self.course.__unicode__(),
            self.lecture.section_code,
            self.tutorial.section_code if self.tutorial is not None else '',
            self.lab.section_code if self.lab is not None else ''])


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