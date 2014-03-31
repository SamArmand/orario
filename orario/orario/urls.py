from django.conf.urls import patterns, include, url

import student
import scheduler
import course_calendar

from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'orario.views.home', name='home'),
    # url(r'^blog/', include('blog.urls')),

    url(r'^admin/', include(admin.site.urls)),
    url(r'^', include('student.urls')),
    url(r'^', include('scheduler.urls')),
    url(r'^', include('course_calendar.urls')),
)
