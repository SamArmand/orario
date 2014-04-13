from django.conf.urls import patterns, url
from django.views.generic import TemplateView

urlpatterns = patterns('',
    url(r'^search/$', 'course_calendar.views.search_courses', name='search-courses'),
)