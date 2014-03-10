from django.db import models
from django.contrib.auth.models import User
from django.utils.translation import ugettext as _
import string


# GEORGE NOTES
#     delete this shizz
#     -- Add Pre/Post/Invariant Everywhere
#     -- Use docstrings under declaration
#     -- TimeField():
#         Time Objects
#
#     What's our input?
#         Student enters desired busy times
#         Student enters desired courses
#     TODOOOO
#         Implement __unicode__ methods for all classes


# As used by Concordia's schedules
MONDAY = 0b1
TUESDAY = 0b10
WEDNESDAY = 0b100
THURSDAY = 0b1000
FRIDAY = 0b10000
SATURDAY = 0b100000
SUNDAY = 0b1000000


class TimeSlot(models.Model):
    label = models.CharField(max_length=50)
    begin_time = models.TimeField()
    end_time = models.TimeField()
    days = models.IntegerField()

    class Meta:
        """
            [Django Metadata Options Class](https://docs.djangoproject.com/en/dev/topics/db/models/#meta-options)
            Modifies the outer class to configure the model for django. Used to make a class abstract
        """
        abstract = True

    def conflicts_with(self, slot):
        """ 
            @param slot: TimeSlot object
            @return: Boolean value, True if TimeField values intersect.
            - Description: Compares self with parameter TimeSlot object.
                Checks if passed parameter occupies the same space as self.
            - Precondition(s): slot must be a valid TimeSlot object => isinstance(slot,TimeSlot)
            - Postcondition(s):none, (does not change state)
        """
        if ((self.days & slot.days)  # Bitwise AND to check for conflicting days
                and ((self.begin_time < slot.end_time) 
                     or (slot.begin_time < self.end_time))):
            return True
        return False


class BusySlot(TimeSlot):
    """
        - Description: BusySlot objects represent periods of time that a user prefers not to alot to school.
        - Precondition(s):
        - Postcondition(s):
    """
    user = models.ForeignKey(User)


class Course(models.Model):
    """
        Represents A Course, which is composed of one or many sections.

    """
    number = models.CharField(max_length=10)  # represented as ID in domain model
    title = models.CharField(max_length=255)  # represented as Name in domain model
    credits = models.DecimalField(max_digits=2, decimal_places=1)  # example: 3.5
    prereqs = models.ManyToManyField("self", symmetrical=False)


class SectionSlot(TimeSlot):
    """
        Contains a Course Object. Has a type of lec, tut, or lab.
        Example: type:lec, code: 'AA', instructor: 'Aiman Hanna',
    """
    section_code = models.CharField(max_length=2)  # "Lect AA" >> Just the AA part
    instructor = models.CharField(max_length=255)  # "Aiman Hanna"
    room = models.CharField(max_length=255)  # "SGW H-530"

    class Meta:
        abstract = True


    @property
    def __unicode__(self):
        return "%s: %s, (%s-%s)" % (self.__class__.__name__, self.section_code, self.begin_time, self.end_time)


    def __init__(self, *args, **kwargs):
        dict = kwargs.pop('dict', None)
        super(SectionSlot, self).__init__(*args, **kwargs)
        if dict is not None:
            self.fill_from_dict(dict)

    def fill_fron_dict(self, dict):
        self.begin_time = dict['begin_time']
        self.end_time = dict['end_time']
        self.days = dict['days']
        self.section_code = dict['section_code']
        self.instructor = dict['instructor']
        self.room = dict['room']
        self.save()

class LectureSlot(SectionSlot):
    pass


class TutorialSlot(SectionSlot):
    pass


class LabSlot(SectionSlot):
    pass


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


class Student(models.Model):
    # wat User is already defined in django.contrib.auth.models
    # has program(program has a sequence), busytimes, courses_taken(record)
    user = models.ForeignKey(User)
    option = models.ForeignKey(Option)
    # busy_times don't need to be defined here
    courses_taken = models.ManyToManyField("record")


# PLAN Make a class CourseList which is a bag of Course Objects.
# Have Schedule, Sequence etc. extend CourseList and implement their own ordering.

class CourseList(models.Model):
    """

    """


class Schedule(models.Model):
    """
    Contains Timeslot objects.
    """


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


class Sequence(CourseList):
    """
        A Collection of Courses ordered by semester. Based on Student(User)'s Program

    """
    user = models.ForeignKey(User)
    program = models.ForeignKey(Program)
    courses = models.ManyToManyField(Course)
