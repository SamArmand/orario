from django.conf.urls import patterns
from django.views.generic import TemplateView

urlpatterns = patterns('',
    (r'^signup/', TemplateView.as_view(template_name="student/signup.html")),
)