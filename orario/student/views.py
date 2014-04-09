from django.shortcuts import render_to_response, HttpResponseRedirect
from django.core.urlresolvers import reverse
from django.template import RequestContext
from django.core.exceptions import PermissionDenied
from forms import ProfileForm

def signup(request):
    render_to_response()

def profile(request):
    if not request.user.is_authenticated():
        raise PermissionDenied

    if request.method == 'POST':
        form = ProfileForm(request.POST)
        if form.is_valid():
            # Validate
            if form.cleaned_data['password0'] != form.cleaned_data['password1']:
                pass  # fuck
            if form.cleaned_data['option'] not in form.cleaned_data['program'].option_set.all():
                pass  # fuck
            if form.cleaned_data['password0']:
                request.user.set_password(form.cleaned_data['password0'])
            request.user.program = form.cleaned_data['program']
            request.user.option = form.cleaned_data['option']
            request.user.save()
            return HttpResponseRedirect(reverse('profile'))
    else:
        print request.user.option
        print request.user.option.program
        form = ProfileForm(
            initial={'program': request.user.option.program,
                     'option': request.user.option})
    return render_to_response(
        'student/edit-profile.html',
        {'form': form},
        context_instance=RequestContext(request))
