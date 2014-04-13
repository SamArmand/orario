from django.shortcuts import render_to_response
from django.template import RequestContext
from django.db.models import Q

from models import Course


def search_courses(request):
    query = request.GET.get('query', None)
    if query:
        courses = Course.objects.filter(Q(number__icontains=query) | Q(title__icontains=query))
    else:
        courses = None
    print repr(courses)
    return render_to_response(
        'course_calendar/search.html',
        {'courses': courses, 'query': query},
        context_instance=RequestContext(request))