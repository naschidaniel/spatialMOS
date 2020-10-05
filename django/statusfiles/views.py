from django.shortcuts import render
from django.shortcuts import get_object_or_404
from django.http import Http404
from django.utils import timezone
from .models import StatusFiles, StatusChecks

# Helper functions
def status_of_check(is_verified_by_admin, max_age, task_finished_time):
    max_age_time = timezone.localtime(timezone.now()) - timezone.timedelta(minutes=max_age)
    print(max_age_time)
    if (task_finished_time >= max_age_time):
        return {'badge_status': 'badge-success', 'status': 'passed'}
    elif not is_verified_by_admin and (task_finished_time >= max_age_time):
        return {'badge_status': 'badge-info', 'status': 'info'}
    elif not is_verified_by_admin and (task_finished_time <= max_age_time):
        return {'badge_status': 'badge-warning', 'status': 'warning'}
    else:
        return {'badge_status': 'badge-danger', 'status': 'failed'}
    
# Views
def systemhealth(request):
    """A view for the latests systemhealth check."""

    def get_all_systemcheck():
        """The function to generate the database query."""
        try:
            return StatusChecks.objects.all()
        except StatusChecks.DoesNotExist:
            raise Http404
    
    systemchecks = get_all_systemcheck()
    systemstatus = []
    for systemcheck in systemchecks:
        statusfile_last = StatusFiles.objects.filter(check_name=systemcheck).latest()
        badge = status_of_check(systemcheck.verified_by_admin, systemcheck.max_age, statusfile_last.task_finished_time)
        systemstatus.append({
                            'name': systemcheck.name, 
                            'task_finished_time': statusfile_last.task_finished_time,
                            'badge': badge,
                            })

    context = {
            'systemstatus': systemstatus,
            'title': 'Systemstatus'
        }

    return render(request, 'statusfiles/systemstatus.html', context)