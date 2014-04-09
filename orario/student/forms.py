from django import forms
from course_calendar.models import Program, Option

class ProfileForm(forms.Form):
    password0 = forms.CharField(required=False, widget=forms.PasswordInput)
    password1 = forms.CharField(required=False, widget=forms.PasswordInput)
    program = forms.ModelChoiceField(queryset=Program.objects.all())
    option = forms.ModelChoiceField(queryset=Option.objects.all())
