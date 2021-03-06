from django.db import models
from django.conf import settings
from django.core.exceptions import ValidationError

import itertools
import logging
logger = logging.getLogger(__name__)

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

    def str_days(self):
        days = ""
        days += "M" if self.days & MONDAY else "-"
        days += "T" if self.days & TUESDAY else "-"
        days += "W" if self.days & WEDNESDAY else "-"
        days += "J" if self.days & THURSDAY else "-"
        days += "F" if self.days & FRIDAY else "-"
        days += "S" if self.days & SATURDAY else "-"
        days += "D" if self.days & SUNDAY else "-"
        return days

    def str_times(self):
        return "%s - %s" % (self.begin_time.strftime('%H:%M'), self.end_time.strftime('%H:%M'))

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
    #: The schedule the BusySlot belongs to.
    schedule = models.ForeignKey('Schedule')


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
    courses = models.ManyToManyField('course_calendar.Course', blank=True)
    #: Auto-generated schedule must contain these sections.
    sections = models.ManyToManyField('course_calendar.Section', blank=True)

    def add_course(self, course):
        """
        Adds course into schedule if all prereqs and coreqs are met.
        Prereqs are either in student's record (student.courses_taken)
        or in a preceding schedule.
        """
        # TODO: Figure out how to check preceding schedules
        from course_calendar.models import Course
        assert isinstance(course, Course)
        # Debug print statements
        # print [prereq in self.student.courses_taken.all() for prereq in course.prereqs.all()]
        # print [coreq in self.courses.all() for coreq in course.coreqs.all()]
        if (course in self.courses.all()):
            return True
        elif (
            all(prereq in self.student.courses_taken.all()
                for prereq in course.prereqs.all())
            and
            all(coreq in itertools.chain(self.courses.all(), self.student.courses_taken.all())
                for coreq in course.coreqs.all())
        ):
            self.courses.add(course)
            return True
        else:
            return False

    def remove_course(self, course):
        from course_calendar.models import Course
        assert isinstance(course, Course)
        self.sections.remove(*[dep.id for dep in self.sections.filter(course__coreqs=course).all()])
        self.sections.remove(*[sec.id for sec in self.sections.filter(course=course).all()])
        self.courses.remove(*[dep.id for dep in Course.objects.filter(coreqs=course).all()])
        self.courses.remove(course)

    def add_section(self, section):
        # TODO conflict checking
        from course_calendar.models import Section
        assert isinstance(section, Section)
        if (
            self.add_course(section.course) and
            section.term == self.term and
            all([not section.conflicts_with(sec) for sec in self.sections.all()]) and
            all([not section.conflicts_with(busy) for busy in self.busyslot_set.all()])
        ):
            self.sections.add(section)
            return True
        return False

    def remove_section(self, section):
        from course_calendar.models import Section
        assert isinstance(section, Section)
        self.sections.remove(section)

    def generate(self):
        """
        Returns a list of courses it failed to schedule.
        :rtype: Course[]
        """
        # TODO zis, noooo
        # Most nasty schedule generating thing evar.
        courses = [section.course for section in self.sections.all()]
        for course in self.courses.all():  # go through courses
            if course in courses:
                pass
            else:
                sections = course.section_set.filter(term=self.term).order_by('?')
                for section in sections:  # try each section in course
                    if self.add_section(section):  # returns true if success
                        break
        freljords = self.courses.exclude(pk__in=[section.course.pk for section in self.sections.all()]).all()
        return freljords