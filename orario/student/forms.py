from django import forms
from course_calendar.models import Program, Option

class ProfileForm(forms.Form):
    password0 = forms.CharField(required=False, widget=forms.PasswordInput)
    password1 = forms.CharField(required=False, widget=forms.PasswordInput)
    option = forms.ModelChoiceField(queryset=Option.objects.order_by("program"))


class LoginForm(forms.Form):
    username = forms.CharField()
    password = forms.CharField(widget=forms.PasswordInput)