from django.db import models
from django.contrib.auth.models import User
from django.utils.translation import ugettext as _

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

class TimeSlot(models.Model):
    label = models.CharField(max_length=50)
    begin_time = models.TimeField()
    end_time = models.TimeField()
    day = models.CharField(max_length=1, choices=DAYS_OF_THE_WEEK)
    
    def conflicts_with(self, slot):
        if ((self.day == slot.day) and ((self.begin_time < slot.end_time) or (slot.begin_time < self.end_time))):
            return true
        return false
    
    class Meta:
        abstract = True

class BusySlot(TimeSlot):
    user = models.ForeignKey(User)
    
class Course(models.Model):
    number = models.CharField(max_length=10)
    title = models.CharField(max_length=255)
    
