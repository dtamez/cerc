from cerc.models import Family
from cerc.forms import ActiveSemesterForm


def semesters(request):
    """Used to populate the dropdown for active semester"""
    form = None
    if request.user.is_authenticated:
        already_selected = request.session.get('active_semester_id')
        form = ActiveSemesterForm(initial={'active_semester':
                                           already_selected})
    return {'active_semester_form': form}


def users(request):
    """Helps us set some flags for the menus"""
    user = request.user
    d = {'is_teacher': False, 'is_family': False, 'is_student': False,
         'is_staff': False, 'family': None}
    if user.is_authenticated():
        if user.groups.filter(name='Teachers'):
            d['is_teacher'] = True
        if user.groups.filter(name='Students'):
            d['is_student'] = True
        if user.groups.filter(name='Families'):
            d['is_family'] = True
            fam = Family.objects.get(user=user)
            d['family_name'] = fam.family_name
            d['show_approve'] = not fam.approved
            d['show_enroll'] = bool(fam.student_set.count()) and fam.approved
            d['show_enroll_menu'] = bool(fam.student_set.count())
        if user.is_staff or user.is_superuser:
            d['is_staff'] = True
    return {'current_user': d}
