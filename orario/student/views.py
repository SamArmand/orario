from django.shortcuts import render_to_response, HttpResponseRedirect, get_object_or_404
from django.core.urlresolvers import reverse
from django.template import RequestContext
from django.core.exceptions import PermissionDenied
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout

from course_calendar.models import Course
from scheduler.forms import CourseForm
from forms import LoginForm, ProfileForm


def login_view(request):
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            user = authenticate(username=form.cleaned_data['username'], password=form.cleaned_data['password'])
            if user is not None:
                if user.is_active:
                    login(request, user)
                    messages.success(request, '<strong>Success!</strong> Logged in as %s.' % user.username)
                    return HttpResponseRedirect(reverse('main'))
                else:
                    messages.error(request, '<strong>Cannot log in.</strong> Your account has been disabled. Contact'
                                            'an administrator for details.')
            else:
                messages.error(request, '<strong>Cannot log in.</strong> Your username and password'
                                        'combination is invalid.')
    else:
        form = LoginForm()
    return render_to_response(
        'student/login.html',
        {'form': form},
        context_instance=RequestContext(request)
    )


def logout_view(request):
    logout(request)
    messages.success(request, '<strong>Success!</strong> Logged out.')
    return HttpResponseRedirect(reverse('login'))


def main_view(request):
    if request.user.is_authenticated():
        fall, fall_created = request.user.schedule_set.get_or_create(term=2)
        winter, winter_created = request.user.schedule_set.get_or_create(term=4)
        summer, summer_created = request.user.schedule_set.get_or_create(term=1)
        return render_to_response(
            'student/main.html',
            {'fall': fall, 'winter': winter, 'summer': summer},
            context_instance=RequestContext(request)
        )
    else:
        messages.warning(request, '<strong>Log in.</strong> You must be logged in to use Orario.')
        return HttpResponseRedirect(reverse('login'))


def profile(request):
    if not request.user.is_authenticated():
        raise PermissionDenied

    record = request.user.courses_taken.all()

    if request.method == 'POST':
        form = ProfileForm(request.POST)
        if form.is_valid():
            # Validate
            if form.cleaned_data['password0']:
                if form.cleaned_data['password0'] != form.cleaned_data['password1']:
                    request.user.set_password(form.cleaned_data['password0'])
                else:
                    messages.error(request, "The two passwords do not match.")
            request.user.option = form.cleaned_data['option']
            request.user.save()
            return HttpResponseRedirect(reverse('profile'))
    else:
        form = ProfileForm(initial={'option': request.user.option})
    return render_to_response(
        'student/edit-profile.html',
        {'form': form, 'record': record},
        context_instance=RequestContext(request))


def add_course_to_record(request):
    if not request.user.is_authenticated():
        raise PermissionDenied

    courses = Course.objects.all()
    if request.method == 'POST':
        form = CourseForm(request.POST, courses=courses)
        if form.is_valid():
            course = form.cleaned_data['course']
            request.user.courses_taken.add(course)
            messages.success(request, "<strong>Success!</strong> Added %s to record." % course)
            return HttpResponseRedirect(reverse('profile'))
    else:
        form = CourseForm(courses=courses)
    return render_to_response(
        'student/add-course-to-record.html',
        {'form': form},
        context_instance=RequestContext(request))


def delete_course_from_record(request, course_id):
    course = get_object_or_404(Course, pk=course_id)
    if not request.user.is_authenticated():
        raise PermissionDenied
    request.user.courses_taken.remove(course)
    messages.error(request, "<strong>Success!</strong> Removed %s from record." % course)
    return HttpResponseRedirect(reverse('profile'))