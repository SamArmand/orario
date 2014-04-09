from django.conf.urls import patterns, url
from django.views.generic import TemplateView

urlpatterns = patterns('',
    url(r'^signup/', TemplateView.as_view(template_name="student/signup.html")),
    url(r'^profile/', 'student.views.profile', name='profile'),
)
