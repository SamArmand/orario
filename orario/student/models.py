from django.contrib.auth.models import AbstractUser
from django.db import models


class Student(AbstractUser):
    option = models.ForeignKey('course_calendar.Option')
    courses_taken = models.ManyToManyField(
        'course_calendar.Course', related_name='students_taken', blank=True, null=True)
    courses_selected = models.ManyToManyField(
        'course_calendar.Course', related_name='students_selected', blank=True, null=True)


