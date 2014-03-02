from django.db import models
from django.contrib.auth.models import User
from django.utils.translation import ugettext as _


"""GEORGE NOTES
    delete this shizz
    -- Add Pre/Post/Invariant Everywhere
    -- Use docstrings under declaration
    -- TimeField():
        Time Objects
"""

# As used by Concordia's schedules
DAYS_OF_THE_WEEK = (
        ('D', _('sunday')),
        ('M', _('monday')),
        ('T', _('tuesday')),
        ('W', _('wednesday')),
        ('J', _('thursday')),
        ('F', _('friday')),
        ('S', _('saturday')),
)


# Types of timeslots in course
COURSE_SLOT_TYPES = (
        ('lec', _('lecture')),
        ('tut', _('tutorial')),
        ('lab', _('lab'))
)

class TimeSlot(models.Model):
    label = models.CharField(max_length=50)
    begin_time = models.TimeField()
    end_time = models.TimeField()
    day = models.CharField(max_length=1, choices=DAYS_OF_THE_WEEK)

    def conflicts_with(self, slot):
        """ 
             
            - Precondition(s): slot must be a valid TimeSlot object => isinstance(slot,TimeSlot)
            - Postcondition(s):none, (does not change state)
        """
        if ((self.day == slot.day)  
                and ((self.begin_time < slot.end_time) 
                     or (slot.begin_time < self.end_time))):
            return True
        return False

    """ 
        Modifies the outer class to configure the model for django.Used to trun a class abstract

    """
    class Meta:
        abstract = True


class BusySlot(TimeSlot):
    """
        - Precondition(s):
        - Postcondition(s):
    """
    user = models.ForeignKey(User)

class Course(models.Model):
    number = models.CharField(max_length=10)
    title = models.CharField(max_length=255)

class CourseSlot(TimeSlot):
    course = models.ForeignKey(Course)
    type = models.CharField(max_length=1, choices=COURSE_SLOT_TYPES)
