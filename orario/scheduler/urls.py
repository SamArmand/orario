from django.conf.urls import patterns, url
from django.views.generic import TemplateView

urlpatterns = patterns('',
        url(r'^schedule/(\d+)/$', 'scheduler.views.schedule', name='schedule'),
        url(r'^schedule/(\d+)/view/$', 'scheduler.views.schedule_view', name='schedule-view'),
        url(r'^schedule/(\d+)/busyslot/$', 'scheduler.views.busyslot', name='busyslot'),
        url(r'^schedule/(\d+)/busyslot/delete/$', 'scheduler.views.delete_busyslot', name='busyslot-delete'),
        url(r'^schedule/(\d+)/course/$', 'scheduler.views.course', name='course'),
        url(r'^schedule/(\d+)/course/delete/$', 'scheduler.views.delete_course', name='course-delete'),
        url(r'^schedule/(\d+)/section/$', 'scheduler.views.section', name='section'),
        url(r'^schedule/(\d+)/section/delete/$', 'scheduler.views.delete_section', name='section-delete'),
        url(r'^schedule/(\d+)/generate/$', 'scheduler.views.generate', name='generate'),
)
