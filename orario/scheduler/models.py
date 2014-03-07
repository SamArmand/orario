from django.db import models
from django.contrib.auth.models import User
from django.utils.translation import ugettext as _


"""GEORGE NOTES
    delete this shizz
    -- Add Pre/Post/Invariant Everywhere
    -- Use docstrings under declaration
    -- TimeField():
        Time Objects

    What's our input?
        Student enters desired busy times
        Student enters desired courses
    TODOOOO
        Implement __unicode__ methods for all classes

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

# Program code to name dictionary
PROGRAM = (
        ('ELEC', _('Electrical Engineering')),
        ('MECH', _('Mechanical Engineering')),
        ('SOEN', _('Software Engineering')),
        ('COEN', _('Computer Engineering')),
        ('BLDG', _('Building Engineering')),
        ('CIVI', _('Civil Engineering')),
        ('COMP', _('Computer Science')),
        ('INDU', _('Industrial Engineering')),
        # Not sure if we should include ENCS, ENGR, etc.
)

class TimeSlot(models.Model):
    label = models.CharField(max_length=50)
    begin_time = models.TimeField()
    end_time = models.TimeField()
    day = models.CharField(max_length=1, choices=DAYS_OF_THE_WEEK)

    """
        [Django Metadata Options Class](https://docs.djangoproject.com/en/dev/topics/db/models/#meta-options)
        Modifies the outer class to configure the model for django. Used to make a class abstract

    """
    class Meta:
        abstract = True

    def conflicts_with(self, slot):
        """ 
            @param slot: TimeSlot object
            @return: Boolean value, True if TimeField values intersect.
            - Description: Compares self with parameter TimeSlot object. Checks if passed parameter occupies the same space as self.
            - Precondition(s): slot must be a valid TimeSlot object => isinstance(slot,TimeSlot)
            - Postcondition(s):none, (does not change state)
        """
        if ((self.day == slot.day)  
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
    number = models.CharField(max_length=10) # represented as ID in domain model
    title = models.CharField(max_length=255) # represented as Name in domain model
    
    credits = models.DecimalField(max_digits=2, decimal_places=1) #  example: 3.5
    prereqs = models.ManyToManyField("self", symmetrical=False)

class CourseSlot(TimeSlot):
    """
        Contains a Course Object. Has a type of lec, tut, or lab.
        Example: type:lec, code: 'AA', instructor: 'Aiman Hanna',
    """
    course = models.ForeignKey(Course)
    section_type = models.CharField(max_length=3, choices=COURSE_SLOT_TYPES) #lec/tut/lab
    
    section = models.Charfield(max_length=2) # "Lect AA" >> Just the AA part
    instructor = models.CharField(max_length=255) # "Aiman Hanna"
    room = models.CharField(max_length=255) # "SGW H-530"



class Student(models.Model):
    # wat User is already defined in django.contrib.auth.models
    # has program(program has a sequence), busytimes, courses_taken(record)
    program = models.ForeignKey(Program)
    # busy_times don't need to be defined here
    courses_taken = models.ManyToManyField("record")


#PLAN Make a class CourseList which is a bag of Course Objects.
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
class Sequence(CourseList):
    """
        A Collection of Courses ordered by semester. Based on Student(User)'s Program

    """
    user = models.ForeignKey(User)
    program = models.CharField(max_length=4,choices=PROGRAM)
    courses = models.ManyToManyField(Course)
