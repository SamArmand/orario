from django.conf.urls import patterns, url
from django.views.generic import TemplateView

urlpatterns = patterns('',
    url(r'^$', 'student.views.main_view', name='main'),
    # url(r'^signup/$', TemplateView.as_view(template_name="student/signup.html")),
    url(r'^login/$', 'student.views.login_view', name='login'),
    url(r'^logout/$', 'student.views.logout_view', name='logout'),
    url(r'^profile/$', 'student.views.profile', name='profile'),
    url(r'^profile/record/$', 'student.views.add_course_to_record', name='course-add-to-record'),
    url(r'^profile/record/(\d+)/delete/$', 'student.views.delete_course_from_record', name='course-delete-from-record')
)
