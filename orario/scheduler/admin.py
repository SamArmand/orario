from django.contrib import admin
from scheduler.models import *

class ScheduleAdmin(admin.ModelAdmin):
    filter_horizontal = ['courses', 'sections',]

admin.site.register(LectureSlot)
admin.site.register(TutorialSlot)
admin.site.register(LabSlot)
admin.site.register(Schedule, ScheduleAdmin)