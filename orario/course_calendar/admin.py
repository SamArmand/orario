from django.contrib import admin
from course_calendar.models import *

class SectionInline(admin.StackedInline):
    model = Section
    extra = 0

class CourseAdmin(admin.ModelAdmin):
    list_display = ('number', 'title',)
    inlines = [SectionInline,]
    filter_horizontal = ('prereqs', 'coreqs',)

admin.site.register(Course, CourseAdmin)
