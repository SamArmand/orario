from django import forms
from django.forms import ModelForm
from course_calendar.models import Course, Section
from models import BusySlot

class BusySlotForm(ModelForm):
    class Meta:
        model = BusySlot
        fields = ['label', 'begin_time', 'end_time', 'days']

class CourseForm(forms.Form):
    course = forms.ModelChoiceField(queryset=Course.objects.all())

    def __init__(self, *args, **kwargs):
        courses = kwargs.pop('courses')
        super(CourseForm, self).__init__(*args, **kwargs)
        self.fields['course'].queryset = courses

class SectionForm(forms.Form):
    section = forms.ModelChoiceField(queryset=Section.objects.all())

    def __init__(self, *args, **kwargs):
        sections = kwargs.pop('sections')
        super(SectionForm, self).__init__(*args, **kwargs)
        self.fields['section'].queryset = sections
