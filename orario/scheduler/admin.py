from django.contrib import admin
from scheduler.models import *

admin.site.register(LectureSlot)
admin.site.register(TutorialSlot)
admin.site.register(LabSlot)
