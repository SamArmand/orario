from django.contrib import admin
from course_calendar.models import *

class SectionInline(admin.StackedInline):
    model = Section
    extra = 0

class CourseAdmin(admin.ModelAdmin):
    inlines = [SectionInline,]

admin.site.register(Course, CourseAdmin)