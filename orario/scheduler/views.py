import json
from django.db.models import Q
from django.http import HttpResponse
from django.core.serializers.json import DjangoJSONEncoder
from django.shortcuts import render_to_response, HttpResponseRedirect, get_object_or_404
from django.core.urlresolvers import reverse
from django.template import RequestContext
from django.core.exceptions import PermissionDenied
from django.contrib import messages
from django.forms.models import model_to_dict

from models import Schedule
from forms import *


def schedule(request, schedule_id):
    schedule_ob = get_object_or_404(Schedule, pk=schedule_id)
    if not (request.user is schedule_ob.student or request.user.is_superuser):
        raise PermissionDenied
    return render_to_response(
        'scheduler/busyslots.html',
        {'schedule': schedule_ob},
        context_instance=RequestContext(request))


def schedule_view(request, schedule_id):
    schedule_ob = get_object_or_404(Schedule, pk=schedule_id)
    if not (request.user is schedule_ob.student or request.user.is_superuser):
        raise PermissionDenied
    response = {'sections': [{
                    'course': model_to_dict(section_ob.course),
                    'lecture': model_to_dict(section_ob.lecture),
                    'tutorial': model_to_dict(section_ob.tutorial) if section_ob.tutorial else None,
                    'lab': model_to_dict(section_ob.lab) if section_ob.lab else None
                } for section_ob in schedule_ob.sections.all()],
                'busyslots': [model_to_dict(slot) for slot in schedule_ob.busyslot_set.all()]}
    return render_to_response(
        'scheduler/schedule.html',
        {'json': json.dumps(response, cls=DjangoJSONEncoder), 'schedule': schedule_ob},
        context_instance=RequestContext(request)
    )


def busyslot(request, schedule_id):
    schedule_ob = get_object_or_404(Schedule, pk=schedule_id)
    if not (request.user is schedule_ob.student or request.user.is_superuser):
        raise PermissionDenied

    if request.method == 'POST':
        form = BusySlotForm(request.POST)
        if form.is_valid():
            slot = form.save(commit=False)
            slot.schedule = schedule_ob
            slot.save()
            messages.success(request, '<strong>Success!</strong> Added event %s.' % slot.label)
            return HttpResponseRedirect(reverse('schedule', args=(schedule_ob.pk,)))
    else:
        form = BusySlotForm()
    return render_to_response(
        'scheduler/busyslot.html',
        {'form': form, 'schedule': schedule_ob},
        context_instance=RequestContext(request))


def delete_busyslot(request, busyslot_id):
    busyslot_ob = get_object_or_404(BusySlot, pk=busyslot_id)
    if not (request.user is busyslot_ob.schedule.student or request.user.is_superuser):
        raise PermissionDenied

    schedule_ob = busyslot_ob.schedule
    busyslot_ob.delete()
    messages.error(request, "<strong>Success!</strong> Deleted event.")
    return HttpResponseRedirect(reverse('schedule', args=(schedule_ob.pk,)))


def course(request, schedule_id):
    schedule_ob = get_object_or_404(Schedule, pk=schedule_id)
    if not (request.user is schedule_ob.student or request.user.is_superuser):
        raise PermissionDenied

    # courses = Course.objects.filter(Q(prereqs=None) | Q(prereqs__in=request.user.courses_taken.all())).all()
    courses = Course.objects.all()
    if request.method == 'POST':
        form = CourseForm(request.POST, courses=courses)
        if form.is_valid():
            course_ob = form.cleaned_data['course']
            result = schedule_ob.add_course(course_ob)
            if result:
                messages.success(request, '<strong>Success!</strong> Added course %s.' % course_ob)
            else:
                messages.error(request, '<strong>Failed to add course.</strong> Prerequisite unsatisfied.')
            return HttpResponseRedirect(reverse('schedule', args=(schedule_ob.pk,)))
    else:
        form = CourseForm(courses=courses)
    return render_to_response(
        'scheduler/course.html',
        {'form': form, 'schedule': schedule_ob},
        context_instance=RequestContext(request))


def delete_course(request, schedule_id, course_id):
    schedule_ob = get_object_or_404(Schedule, pk=schedule_id)
    course_ob = get_object_or_404(Course, pk=course_id)
    if not (request.user is schedule_ob.student or request.user.is_superuser):
        raise PermissionDenied
    schedule_ob.remove_course(course_ob)
    messages.error(request, "<strong>Success!</strong> Removed course.")
    return HttpResponseRedirect(reverse('schedule', args=(schedule_ob.pk,)))


def section(request, schedule_id):
    schedule_ob = get_object_or_404(Schedule, pk=schedule_id)
    if not (request.user is schedule_ob.student or request.user.is_superuser):
        raise PermissionDenied

    sections = Section.objects.\
        filter(course__in=schedule_ob.courses.all()).\
        filter(term=schedule_ob.term).\
        exclude(schedule=schedule_ob).all()
    if request.method == 'POST':
        form = SectionForm(request.POST, sections=sections)
        if form.is_valid():
            section_ob = form.cleaned_data['section']
            result = schedule_ob.add_section(section_ob)
            if result:
                messages.success(request, '<strong>Success!</strong> Added section %s.' % section_ob)
                return HttpResponseRedirect(reverse('schedule', args=(schedule_ob.pk,)))
            else:
                raise PermissionDenied
    else:
        form = SectionForm(sections=sections)
    return render_to_response(
        'scheduler/section.html',
        {'form': form, 'schedule': schedule_ob},
        context_instance=RequestContext(request))


def delete_section(request, schedule_id, section_id):
    schedule_ob = get_object_or_404(Schedule, pk=schedule_id)
    section_ob = get_object_or_404(Section, pk=section_id)
    if not (request.user is schedule_ob.student or request.user.is_superuser):
        raise PermissionDenied
    schedule_ob.remove_section(section_ob)
    messages.error(request, "<strong>Success!</strong> Removed section.")
    return HttpResponseRedirect(reverse('schedule', args=(schedule_ob.pk,)))


def generate(request, schedule_id):
    schedule_ob = get_object_or_404(Schedule, pk=schedule_id)
    if not (request.user is schedule_ob.student or request.user.is_superuser):
        raise PermissionDenied
    freljords = schedule_ob.generate()
    if freljords:
        messages.warning(request,
                         "<strong>Success!</strong> Schedule generated. Failed to add following courses: %s."
                         % ", ".join([freljord.__unicode__() for freljord in freljords]))
    else:
        messages.success(request,
                         "<strong>Success!</strong> Schedule generated. Added all courses.")
    return HttpResponseRedirect(reverse('schedule', args=(schedule_ob.pk,)))


def auto_generate(request, schedule_id):
    schedule_ob = get_object_or_404(Schedule, pk=schedule_id)
    if not (request.user is schedule_ob.student or request.user.is_superuser):
        raise PermissionDenied
    num_courses = 5 - schedule_ob.courses.count()
    if request.user.option:
        for course in request.user.option.get_next_courses(request.user):
            result = schedule_ob.add_course(course)
            if result:
                num_courses -= 1
            if num_courses <= 0:
                break
    else:
        messages.warning(request,
                         "<strong>Warning!</strong> You have not selected a program option yet.")
    freljords = schedule_ob.generate()
    if freljords:
        messages.warning(request,
                         "<strong>Success!</strong> Schedule generated. Failed to add following courses: %s."
                         % ", ".join([freljord.__unicode__() for freljord in freljords]))
    else:
        messages.success(request,
                         "<strong>Success!</strong> Schedule generated. Added all courses.")
    return HttpResponseRedirect(reverse('schedule', args=(schedule_ob.pk,)))