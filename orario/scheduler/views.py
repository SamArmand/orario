from django.http import HttpResponse
import json
from django.core.serializers.json import DjangoJSONEncoder
from django.shortcuts import render_to_response, HttpResponseRedirect, get_object_or_404
from django.core.urlresolvers import reverse
from django.template import RequestContext
from django.core.exceptions import PermissionDenied
from django.contrib import messages
from django.core import serializers
from django.forms.models import model_to_dict
from scheduler.models import Schedule, BusySlot
from forms import *


def schedule(request, schedule_id):
    schedule = get_object_or_404(Schedule, pk=schedule_id)
    if not (request.user is schedule.student or request.user.is_superuser):
        raise PermissionDenied
    return render_to_response(
        'scheduler/busyslots.html',
        {'schedule': schedule},
        context_instance=RequestContext(request))

def time_handler(obj):
    return obj.isoformat() if hasattr(obj, 'isoformat') else obj

def schedule_view(request, schedule_id):
    schedule = get_object_or_404(Schedule, pk=schedule_id)
    if not (request.user is schedule.student or request.user.is_superuser):
        raise PermissionDenied
    response = {}
    response['schedule'] = model_to_dict(schedule)
    sections = [{
        'section': model_to_dict(section),
        'lecture': model_to_dict(section.lecture),
        'tutorial': model_to_dict(section.tutorial) if section.tutorial else None,
        'lab': model_to_dict(section.lab) if section.lab else None
    } for section in schedule.sections.all()]
    response['sections'] = sections
    return HttpResponse(json.dumps(response, cls=DjangoJSONEncoder), content_type="application/json")

def busyslot(request, schedule_id):
    schedule = get_object_or_404(Schedule, pk=schedule_id)
    if not (request.user is schedule.student or request.user.is_superuser):
        raise PermissionDenied

    if request.method == 'POST':
        form = BusySlotForm(request.POST)
        if form.is_valid():
            slot = form.save(commit=False)
            slot.schedule = schedule
            slot.save()
            messages.success(request, '<strong>Success!</strong> Added event %s.' % slot.label)
            return HttpResponseRedirect(reverse('schedule', args=(schedule.pk,)))
    else:
        form = BusySlotForm()
    return render_to_response(
        'scheduler/busyslot.html',
        {'form': form, 'schedule': schedule},
        context_instance=RequestContext(request))

def delete_busyslot(request, busyslot_id):
    busyslot = get_object_or_404(BusySlot, pk=busyslot_id)
    if not (request.user is busyslot.schedule.student or request.user.is_superuser):
        raise PermissionDenied

    schedule = busyslot.schedule
    busyslot.delete()
    messages.error(request, "<strong>Success!</strong> Deleted event.")
    return HttpResponseRedirect(reverse('schedule', args=(schedule.pk,)))


def course(request, schedule_id):
    schedule = get_object_or_404(Schedule, pk=schedule_id)
    if not (request.user is schedule.student or request.user.is_superuser):
        raise PermissionDenied

    # TODO courses = Course.objects.filter(prereqs__in=request.user.courses_taken.all())
    courses = Course.objects.all()
    if request.method == 'POST':
        form = CourseForm(request.POST, courses=courses)
        if form.is_valid():
            course = form.cleaned_data['course']
            result = schedule.add_course(course)
            if result:
                messages.success(request, '<strong>Success!</strong> Added course %s.' % course)
                return HttpResponseRedirect(reverse('schedule', args=(schedule.pk,)))
            else:
                raise PermissionDenied
    else:
        form = CourseForm(courses=courses)
    return render_to_response(
        'scheduler/course.html',
        {'form': form, 'schedule': schedule},
        context_instance=RequestContext(request))

def delete_course(request, schedule, course):
    pass

def section(request, schedule):
    pass

def delete_section(request, schedule, section_id):
    pass

def generate(request, schedule_id):
    schedule = get_object_or_404(Schedule, pk=schedule_id)
    if not (request.user is schedule.student or request.user.is_superuser):
        raise PermissionDenied
    freljords = schedule.generate()
    if freljords:
        messages.warning(request,
            "<strong>Success!</strong> Schedule generated. Failed to add following courses: %s."
            % ", ".join([freljord.__unicode__() for freljord in freljords]))
    else:
        messages.success(request,
            "<strong>Success!</strong> Schedule generated. Added all courses.")
    return HttpResponseRedirect(reverse('schedule', args=(schedule.pk,)))
