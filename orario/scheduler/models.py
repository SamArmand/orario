from django.db import models
from django.conf import settings

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
    user = models.ForeignKey(settings.AUTH_USER_MODEL)


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

    def __unicode__(self):
        return "%s: %s, (%s-%s)" % (self.__class__.__name__, self.section_code, self.begin_time, self.end_time)

    def __init__(self, *args, **kwargs):
        sect_dict = kwargs.pop('sect_dict', None)
        super(SectionSlot, self).__init__(*args, **kwargs)
        if sect_dict is not None:
            self.fill_from_dict(sect_dict)

    def fill_from_dict(self, sect_dict):
        self.begin_time = sect_dict['begin_time']
        self.end_time = sect_dict['end_time']
        self.days = sect_dict['days']
        self.section_code = sect_dict['section_code']
        self.instructor = sect_dict['instructor']
        self.room = sect_dict['room']
        self.save()


class LectureSlot(SectionSlot):
    pass


class TutorialSlot(SectionSlot):
    pass


class LabSlot(SectionSlot):
    pass


class Schedule(models.Model):
    """
    Contains Timeslot objects.
    """
