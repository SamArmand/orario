from django.contrib import admin
from course_calendar.models import *

class SectionInline(admin.StackedInline):
    model = Section
    extra = 0

class CourseAdmin(admin.ModelAdmin):
    list_display = ('number', 'title',)
    inlines = [SectionInline,]
    filter_horizontal = ('prereqs', 'coreqs',)

class OptionInline(admin.StackedInline):
    model = Option
    extra = 1

class ProgramAdmin(admin.ModelAdmin):
    inlines = [OptionInline,]

admin.site.register(Course, CourseAdmin)
admin.site.register(Program, ProgramAdmin)
