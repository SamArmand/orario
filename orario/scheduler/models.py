from django.db import models
from django.conf import settings
from django.core.exceptions import ValidationError

import logging
logger = logging.getLogger(__name__)

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

MONDAY = 0b1
TUESDAY = 0b10
WEDNESDAY = 0b100
THURSDAY = 0b1000
FRIDAY = 0b10000
SATURDAY = 0b100000
SUNDAY = 0b1000000


def validate_days(days):
    """Validator to check if the days int is within range."""
    assert isinstance(days, int)
    if days < 0 or days > 0b1111111:
        raise ValidationError('days out of range')


class TimeSlot(models.Model):
    """
    Abstract class representing a time slot in a schedule.
    """
    #: A generic label that can be used by child classes.
    label = models.CharField(max_length=50)
    #: The starting time of the itme slot.
    begin_time = models.TimeField()
    #: The ending time of the time slot.
    end_time = models.TimeField()
    #: Bitwise representation of the days of the week where the time slot exists.
    days = models.IntegerField(validators=[validate_days])

    class Meta:
        """
        [Django Metadata Options Class](https://docs.djangoproject.com/en/dev/topics/db/models/#meta-options)
        Modifies the outer class to configure the model for django. Used to make a class abstract
        """
        abstract = True

    def conflicts_with(self, slot):
        """
        Returns whether this TimeSlot conflicts with the specified
        slot.
        :type slot: TimeSlot
        :rtype : bool
        """
        if slot is None:
            return False
        assert isinstance(slot, TimeSlot)
        if self.days & slot.days:  # Bitwise AND to check for conflicting days
            return self.wraps(slot) or slot.wraps(self)
        return False

    def wraps(self, slot):
        """
        Returns whether this TimeSlot is wraps another.
        :type slot: TimeSlot
        :rtype: bool
        """
        assert isinstance(slot, TimeSlot)
        if (self.begin_time < slot.begin_time < self.end_time
            or slot.begin_time < self.end_time < slot.end_time):
            return True
        else:
            return False


class BusySlot(TimeSlot):
    """
    A specialized class representing periods of time that a user prefers not
    to allot to school.
    """
    #: The student the BusySlot belongs to.
    student = models.ForeignKey(settings.AUTH_USER_MODEL)


class SectionSlot(TimeSlot):
    """
    An abstract class that represents a class section.
    """
    #: The code for the section, e.g. "AA"
    section_code = models.CharField(max_length=2)
    #: The instructor for the section.
    instructor = models.CharField(max_length=255, null=True, blank=True)
    #: The room number for the section.
    room = models.CharField(max_length=255)

    class Meta:
        abstract = True

    def __unicode__(self):
        """Returns the section as a string, with basic info."""
        return "%s: %s, (%s-%s)" % (self.__class__.__name__,
                                    self.section_code,
                                    self.begin_time.strftime('%H:%M'),
                                    self.end_time.strftime('%H:%M'))

    def __init__(self, *args, **kwargs):
        """
        Custom constructor that can construct an object with the
        specified dictionary.
        """
        sect_dict = kwargs.pop('sect_dict', None)
        super(SectionSlot, self).__init__(*args, **kwargs)
        if sect_dict is not None:
            self.fill_from_dict(sect_dict)

    def fill_from_dict(self, sect_dict):
        """
        Fills the section with values from the specified dictionary.
        """
        self.begin_time = sect_dict['begin_time']
        self.end_time = sect_dict['end_time']
        self.days = sect_dict['days']
        self.section_code = sect_dict['section_code']
        self.instructor = sect_dict['instructor']
        self.room = sect_dict['room']
        self.save()


class LectureSlot(SectionSlot):
    """
    A specialized SectionSlot that represents a lecture.
    """
    pass


class TutorialSlot(SectionSlot):
    """
    A specialized SectionSlot that represents a tutorial.
    """
    pass


class LabSlot(SectionSlot):
    """
    A specialized SectionSlot that represents a lab.
    """
    pass


class Schedule(models.Model):
    """
    Holds schedule information for a single school term.
    Responsible for populating itself given set constraints.
    """
    #: The student who owns the schedule.
    student = models.ForeignKey(settings.AUTH_USER_MODEL)
    #: The term number as per Concordia University's conventions.
    term = models.IntegerField()
    #: Auto-generated schedule must contain these courses.
    courses = models.ManyToManyField('course_calendar.Course')
    #: Auto-generated schedule must contain these sections.
    sections = models.ManyToManyField('course_calendar.Section')

    def add_course(self, course):
        """
        Adds course into schedule if all prereqs and coreqs are met.
        Prereqs are either in student's record (student.courses_taken)
        or in a preceding schedule.
        """
        # TODO: Figure out how to check preceding schedules
        from course_calendar.models import Course
        assert isinstance(course, Course)
        print [prereq in self.student.courses_taken.all() for prereq in course.prereqs.all()]
        print [coreq in self.courses.all() for coreq in course.coreqs.all()]
        if (
            all(prereq in self.student.courses_taken.all() for prereq in course.prereqs.all())
            and
            all(coreq in self.courses.all() for coreq in course.coreqs.all())
        ):
            self.courses.add(course)
            return True
        else:
            return False

    def remove_course(self, course):
        # TODO but u test?
        from course_calendar.models import Course
        assert isinstance(course, Course)
        self.courses.remove([Course.objects.filter(coreqs__contains=course), course])

    def add_section(self, section):
        # TODO conflict checking
        # TODO but u test?
        from course_calendar.models import Section
        assert isinstance(section, Section)
        if (self.add_course(section.course)):
            self.sections.add(section)
            return True
        else:
            return False

    def remove_section(self, section):
        # TODO but u test? i liek nasty coed
        from course_calendar.models import Section
        assert isinstance(section, Section)
        self.sections.remove([
            Section.objects.filter(course__coreqs__contains=section.course),
            section
        ])

    def generate(self):
        """
        Returns a list of courses it failed to schedule.
        :rtype: Course[]
        """
        # TODO zis, noooo
        # Most nasty schedule generating thing evar.
        freljords = []
        for course in self.courses.all():  # go through courses
            if course in [section.course for section in self.sections]:
                pass
            else:
                sections = course.section_set.all()
                section_count = len(sections)
                for section in sections:  # try each section in course
                    section_count -= 1
                    if self.add_section(section):  # returns true if success
                        break
                if section_count == 0:
                    freljords.append(course)
        return freljords