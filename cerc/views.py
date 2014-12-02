'''
Created on Aug 1, 2009

@author: dtamez
'''
from calendar import monthrange
from datetime import (
    date,
    datetime,
    timedelta,
)
import json
import smtplib
import uuid

from django.contrib.auth.decorators import login_required
from django.core.exceptions import MultipleObjectsReturned
from django.core.mail import send_mail
from django.core.urlresolvers import reverse
from django.http import (
    HttpResponse,
    HttpResponseRedirect,
    HttpResponseNotFound,
)
from django.shortcuts import (
    render_to_response,
    redirect,
    get_object_or_404,
)

from django.template import RequestContext
from django.template.loader import render_to_string
from django.utils.safestring import mark_safe
# from django_ajax.decorators import ajax

from cerc.utils import AssignmentCalendar
from cerc.forms import (
    AddressForm,
    AssignmentForm,
    ChangeUnitAssignmentDatesForm,
    ContactInfoForm,
    CopyAssignmentsForm,
    CourseDetailsForm,
    CourseSubmissionForm,
    EmailForm,
    FamilyForm,
    FatherForm,
    MotherForm,
    StudentForm,
    StudentAssignmentForm,
    TeacherBioForm,
    TeacherRequestForm,
    UnitForm,
    UnitGradeForm,
    UserForm,
)
from cerc.models import (
    Assignment,
    Attendance,
    ContactInfo,
    Course,
    Enrollment,
    Family,
    Message,
    Semester,
    Student,
    StudentAssignment,
    StudentUnit,
    Teacher,
    Unit,
)


# External api
# Login and registration
def index(request):
    context = RequestContext(request)
    user = request.user
    if user.is_authenticated():

        current_user = context['current_user']
        if current_user['is_teacher']:
            teacher = Teacher.objects.get(user=user)
            return index_teacher(request, teacher)
        elif current_user['is_student']:
            student = Student.objects.get(user=user)
            return index_student(request, student)
        elif current_user['is_family']:
            return index_family(request, user)
        elif current_user['is_staff']:
            return HttpResponseRedirect('/admin')
    return redirect('accounts/login/', context_instance=context)


def index_teacher(request, teacher):
    context = RequestContext(request)
    t = {'name': teacher.contact_info.full_name}
    context['teacher'] = t

    return render_to_response('index_teacher.html', context_instance=context)


def index_student(request, student):
    context = RequestContext(request)
    s = {'name': student.student.full_name}
    context['student'] = s

    return render_to_response('index_student.html', context_instance=context)


def index_family(request, user):
    context = RequestContext(request)
    return render_to_response('index_family.html', context_instance=context)


@login_required
def upcoming_courses(request):
    context = RequestContext(request)
    user = request.user
    teacher = get_object_or_404(Teacher, user=user)
    t = {'name': teacher.contact_info.full_name}
    upcoming = get_upcoming_semesters()
    for semester_id in upcoming:
        t['upcoming'] = get_courses_for_semester_and_teacher(
            semester_id, teacher.id)
    context['teacher'] = t

    return render_to_response('upcoming_courses.html',
                              context_instance=context)


@login_required
def current_courses(request):
    context = RequestContext(request)
    user = request.user
    teacher = get_object_or_404(Teacher, user=user)
    t = {'name': teacher.contact_info.full_name}
    current = get_active_semester(request)
    t['current'] = get_courses_for_semester_and_teacher(
        current.id, teacher.id)
    context['teacher'] = t

    return render_to_response('current_courses.html', context_instance=context)


def get_courses_for_semester_and_teacher(semester_id, teacher_id):
    upcoming = []
    courses = Course.objects.filter(semester__id=semester_id,
                                    teachers__id=teacher_id)
    for course in courses:
        upcoming.append(course)
    return upcoming


def get_courses_for_semester_and_student(semester_id, student_id,
                                         get_assignments=True):
    enrollments = (Enrollment.objects.filter(course__semester__id=semester_id)
                   .filter(student__id=student_id))
    courses = []
    for enrollment in enrollments:
        course = enrollment.course
        enrollment.course.teacher_names = get_teachers_names(course)
        if get_assignments:
            course.units = get_student_assignments(student_id, course)
        courses.append(enrollment.course)
    return courses


def get_teachers_names(course):
    names = []
    for teacher in course.teachers.all():
        names.append(teacher.contact_info.full_name)
    return ", ".join(names)


def get_or_create_assignment_no_dups(student_id, ca):
    # Got some bad data because of a different bug - help clean it up..
    # remove all but the first
    try:
        sa, created = (StudentAssignment.objects
                       .get_or_create(student_id=student_id,
                                      assignment=ca))
    except MultipleObjectsReturned:
        dups = StudentAssignment.objects.filter(student__id=student_id,
                                                assignment=ca)
        sa = get_first_and_eliminate_the_rest(dups)
    return sa


def get_first_and_eliminate_the_rest(dups):
    first = None
    for n, dup in enumerate(dups):
        if n == 0:
            first = dup
        else:
            dup.delete()
    return first


def get_student_assignments(student_id, course, start=None, end=None):
    course_assignments = (Assignment.objects
                          .filter(unit__course=course)
                          .order_by('due_date'))
    if start and end:
        course_assignments = (course_assignments
                              .filter(due_date__gte=start)
                              .filter(due_date__lte=end)
                              .order_by('due_date'))
    if not len(course_assignments):
        return None
    # for each course_assignment get all units
    # for each unit get all student_assignments
    # create the student_assignment if it doesn't already exist
    units_qs = Unit.objects.filter(course=course).order_by('date')
    units = []
    for idx, unit in enumerate(units_qs):
        unit_course_assignments = (course_assignments.filter(unit=unit)
                                   .order_by('due_date'))
        student_assignments = []
        for ca in unit_course_assignments:
            sa = get_or_create_assignment_no_dups(student_id, ca)
            student_assignments.append(sa)
        unit.student_assignments = student_assignments
        try:
            unit.student_unit, created = (StudentUnit.objects
                                          .get_or_create(student_id=student_id,
                                                         unit=unit))
        except MultipleObjectsReturned:
            dups = (StudentUnit.objects
                    .filter(student__id=student_id, unit=unit))
            unit.student_unit = get_first_and_eliminate_the_rest(dups)

        units.append(unit)
    return units


def get_calendar_assignments(request, student_id, year, month):
    # get the students courses
    semester = get_active_semester(request)
    courses = (Course.objects
               .filter(semester__id=semester.id)
               .filter(enrollment__student__id=student_id)
               .distinct())
    # get all CourseAssignments for these courses in the given month (order by
    # date)
    start = date(year, month, 1)
    _, last = monthrange(year, month)
    end = date(year, month, last)
    assignments = (Assignment.objects
                   .filter(unit__course__in=courses)
                   .filter(due_date__gte=start)
                   .filter(due_date__lte=end)
                   .order_by('due_date'))
    # get or create the student assignments
    student_assignments = []
    for ca in assignments:
        sa, created = (StudentAssignment.objects
                       .get_or_create(student_id=student_id, assignment=ca))
        student_assignments.append(sa)
    return student_assignments


def activate_semester(request, id):
    request.session['active_semester_id'] = id
    return HttpResponse('')


def get_active_semester(request):
    id = request.session.get('active_semester_id')
    try:
        semester = Semester.objects.get(pk=id)
    except Semester.DoesNotExist:
        semester = get_current_semester()
        request.session['active_semester_id'] = semester.id
    return semester


def get_current_semester():
    today = date.today
    semesters = (Semester.objects
                 .filter(end_date__gte=today)
                 .filter(start_date__lte=today))
    if semesters:
        return semesters[0]
    else:
        # no current semester - use the latest one instead
        semesters = (Semester.objects.all().exclude(start_date=None)
                     .order_by('-start_date'))
        return semesters[0]


def get_upcoming_semesters():
    semesters = Semester.objects.filter(start_date__gte=date.today)
    results = []
    for semester in semesters:
        results.append(semester.id)
    return results


def signin(request, student_id):
    """Takes the student that is signing in and marks the student as attending
    all classes he is enrolled in for that day
    """
    student_id = int(student_id)
    return HttpResponse("Signin for student %d" % student_id)


# Enrollment


@login_required
def enroll_student(request, student_id, class_id):
    """Enrolls a student in one class.  If payment information is provided then
    the student's spot is paid for and guaranteed.  If no payment information
    is provided then the student is not guaranteed a spot and may lost it if
    others pay for available slots before payment is received for this student.
    """
    pass


@login_required
def drop_student(request, student_id, class_id):
    """Drops a student from one class.  If payment information is provided then
    the student's account is settled for that class.  If no payment information
    is provided then the student has an outstanding debit for the class.
    """
    pass


# Courses


def course(request, code):
    course = Course.objects.filter(code=code).order_by('-semester__start_date')
    context = RequestContext(request)
    if course:
        context['course'] = course[0]
        return render_to_response('course.html', context_instance=context)
    else:
        return HttpResponse('No course with code %s was found' % code)


@login_required
def submit_course(request):
    """Lets a teacher create a course and submit it for approval by the board.
    If the board approves then the class is eligible for enrollments.
    """
    if request.method == 'POST':
        form = CourseSubmissionForm(request.POST)
        if form.is_valid():
            course_submission = form.save(commit=False)
            course_submission.save()
            form.save_m2m()

            return HttpResponseRedirect('/course_submitted')
    else:
        form = CourseSubmissionForm()

    context = RequestContext(request)
    context['form'] = form
    return render_to_response('submit_course.html', context_instance=context)


def course_submitted(request):
    return render_to_response('course_submitted.html',
                              context_instance=RequestContext(request))


@login_required
def edit_course_details(request, id):
    """Lets a teacher edit the course destails before the class starts.  """
    course = get_object_or_404(Course, pk=id)
    if request.method == 'POST':
        form = CourseDetailsForm(request.POST, instance=course)
        if form.is_valid():
            form.save()

            return HttpResponseRedirect('/course_submitted')
    else:
        form = CourseDetailsForm(instance=course)

    context = RequestContext(request)
    context['form'] = form
    context['id'] = id
    return render_to_response('edit_course.html', context_instance=context)


@login_required
def submit_contact_info(request):
    """Lets a user create and/or edit their contact information.  """
    user = request.user
    info = None
    address = None
    if user.groups.filter(name='Teachers'):
        teacher = Teacher.objects.get(user=user)
        info = teacher.contact_info
        address = teacher.address
    elif user.groups.filter(name="Students"):
        student = Student.objects.get(user=user)
        info = student.student
        address = student.family.address
    elif user.groups.filter(name="Families"):
        family = Family.objects.get(user=user)
        info = family.mother
        address = family.address
    if request.method == 'POST':
        contact_info_form = ContactInfoForm(request.POST, instance=info)
        address_form = AddressForm(request.POST, instance=address)
        if contact_info_form.is_valid() and address_form.is_valid():
            contact_info_form.save()
            address_form.save()
            return HttpResponseRedirect('/contact_info_submitted')
    else:
        contact_info_form = ContactInfoForm(instance=info)
        address_form = AddressForm(instance=address)
    context = RequestContext(request)
    return render_to_response('submit_contact_info.html',
                              {'contact_info_form': contact_info_form,
                               'address_form': address_form},
                              context_instance=context)


def contact_info_submitted(request):
    return render_to_response('contact_info_submitted.html',
                              context_instance=RequestContext(request))


@login_required
def edit_teacher_bio(request):
    """Lets a teacher edit their own bio.  """
    user = request.user
    teacher = Teacher.objects.get(user=user)
    if request.method == 'POST':
        form = TeacherBioForm(request.POST, instance=teacher)
        if form.is_valid():
            form.save()

            return HttpResponseRedirect('/teacher_bio_submitted')
    else:
        form = TeacherBioForm(instance=teacher)

    context = RequestContext(request)
    context['form'] = form
    context['id'] = id
    return render_to_response('edit_teacher_bio.html',
                              {'form': form},
                              context_instance=context)


def teacher_bio_submitted(request):
    return render_to_response('teacher_bio_submitted.html',
                              context_instance=RequestContext(request))


def get_teacher_bio(request, username):
    try:
        teacher = Teacher.objects.get(user__username=username)
        bio = teacher.bio
    except Teacher.DoesNotExist:
        bio = ''
    return HttpResponse(bio)


def submit_teacher_request(request):
    """Accepts requests to become a cerc teacher"""
    if request.method == 'POST':
        form = TeacherRequestForm(request.POST)
        if form.is_valid():
            form.save()
            msg = render_to_string('email_teacher_request.txt',
                                   form.cleaned_data)
            try:
                to = ['Cerc Administrator <education@cerconline.org>']
                send_mail('CERC Teacher Request', msg,
                          'noreply@enroll-cerconline.org',
                          to,
                          fail_silently=False)
            except smtplib.SMTPException, e:
                print e.message
            return HttpResponseRedirect('/teacher_request_submitted')
    else:
        form = TeacherRequestForm()
    context = RequestContext(request)
    return render_to_response('submit_teacher_request.html',
                              {'form': form},
                              context_instance=context)


def teacher_request_submitted(request):
    return render_to_response('teacher_request_submitted.html',
                              context_instance=RequestContext(request))


# Reports


def _get_attendance_info(request, weekday=None, when=None):
    days = ['Mo', 'Tu', 'We', 'Th', 'Fr', 'Sa', 'Su']
    today = date.today()
    if when:
        today = when
    if not weekday:
        weekday = days[today.weekday()]
    else:
        weekday = days[int(weekday)]

    enrollments = (Enrollment.objects
                   .filter(course__semester__start_date__lte=today)
                   .filter(course__semester__end_date__gte=today)
                   .filter(drop_date=None)
                   .filter(course__day__contains=weekday)
                   .filter(drop_date=None)
                   .order_by('student__student__last_name',
                             'student__student__first_name', 'course__time'))

    previous_student = None
    students = []
    odd_even = True
    for enrollment in enrollments:
        if (previous_student and previous_student['name'] ==
                enrollment.student.student.__str__()):
            previous_student['courses'].append({
                'name': enrollment.course.title,
                'id': enrollment.course.id})
        else:
            attendance = None
            try:
                attendance = Attendance.objects.filter(
                    student=enrollment.student,
                    course=enrollment.course,
                    date=today)
            except Attendance.DoesNotExist:
                pass
            previous_student = {'id': enrollment.student.id,
                                'class': 'odd' if odd_even else 'even',
                                'name': enrollment.student.student.__str__(),
                                'attended': True if attendance else False,
                                'courses': [{'name': enrollment.course.title,
                                             'id': enrollment.course.id}]}
            students.append(previous_student)
            odd_even = not odd_even

    return {'students': students}


def mark_attendance(request):
    data = json.loads(request.POST.get('vals'))
    student_id = data.get('student_id')
    course_ids = data.get('course_ids')
    today = date.today()
    for course_id in course_ids:
        attendance = Attendance()
        attendance.student = Student.objects.get(id=student_id)
        course = Course.objects.get(id=course_id)
        attendance.course = course
        attendance.date = today
        attendance.save()

    return HttpResponse('')


def attendance(request, year=None, month=None, day=None):
    today = date.today()
    if year and month and day:
        try:
            today = date(int(year), int(month), int(day))
        except:
            pass
    results = _get_attendance_info(request, date=today)
    results['today'] = today
    return render_to_response('daily_attendance.html', {'results': results})


def attendance_sheet(request):
    results = _get_attendance_info(request)
    # TODO: return correct date if weekday passed in
    results['today'] = date.today()
    return render_to_response('attendance.html', {'results': results})


def attendance_info(request):
    results = _get_attendance_info(request)
    encoder = json.JSONEncoder()
    return HttpResponse(encoder.encode(results))


# Internal api


def upcoming_classes(request):
    """A list of courses for the upcoming semester to help with enrollment."""
    results = []
    courses = Course.objects.filter(start_date__gt=date(2009, 8, 23))
    for course in courses:
        teachers = [teacher.contact_info.__str__()
                    for teacher in course.teachers.all()]
        result = {'code': course.code, 'title': course.title,
                  'materials_fee': course.materials_fee, 'teachers': teachers,
                  'tuition': course.tuition}
        results.append(result)
    return render_to_response('upcoming_classes.html', {'results': results})


def enrollment_by_family(request):
    context = RequestContext(request)
    families = Family.objects.all().order_by('family_name')
    semester_id = request.POST['semester']
    semester = Semester.objects.get(pk=semester_id)
    fams = []
    for family in families:
        family.mother = family.mother or ContactInfo()
        family.father = family.father or ContactInfo()
        fam = {}
        fam['name'] = family.family_name
        fam['mother'] = family.mother.first_name
        fam['father'] = family.father.first_name
        fam['phone'] = family.mother.phone
        fam['phone2'] = family.father.phone
        fam['email'] = family.mother.email
        fams.append(fam)
        students = family.student_set.all().order_by('student__first_name')
        studs = []
        fam["students"] = studs
        for student in students:
            stud = {'name': student.student.first_name}
            studs.append(stud)
            enrollments = (Enrollment.objects
                           .filter(student__id=student.id)
                           .filter(course__semester__id=semester_id)
                           .filter(drop_date=None)
                           .order_by('course'))
            if enrollments:
                courses = []
                stud['courses'] = courses
                for enrollment in enrollments:
                    course = {'name': enrollment.course.title}
                    courses.append(course)
            else:
                studs.remove(stud)
        if not studs:
            fams.remove(fam)

    context['fams'] = fams
    context['semester_name'] = semester.name
    return render_to_response('enrollment_by_family.html',
                              context_instance=context)


def enrollment_for_teacher(teacher, semester_id):
    results = []
    enrollments = (Enrollment.objects
                   .filter(course__teachers__id=teacher.id)
                   .filter(course__semester__id=semester_id)
                   .filter(drop_date=None)
                   .order_by('course', 'student__student__first_name',
                             'student__student__last_name'))
    courses = []
    if enrollments:
        t = {}
        results.append(t)
        t['name'] = teacher.contact_info.__str__()
        t['courses'] = courses

    last_course = None
    for enrollment in enrollments:
        if courses:
            last_course = courses[-1]
        if not last_course or last_course['id'] != enrollment.course.id:
            course = {'title': enrollment.course.title, 'students': [],
                      'id': enrollment.course.id}
            courses.append(course)
            last_course = course

        last_course = courses[-1]
        last_course['students'].append(enrollment.student)
        last_course['num_students'] = len(last_course['students'])
    return results


def render_enrollment_by_teacher(request):
    """Provides a list of students enrolled in each class.  This information is
    then used to pay teachers the appropriate amount for each class.
    """
    context = RequestContext(request)
    results = []
    teachers = Teacher.objects.all()
    semester_id = request.POST['semester']
    semester = Semester.objects.get(pk=semester_id)
    for teacher in teachers:
        results.extend(enrollment_for_teacher(teacher, semester_id))

    context['results'] = results
    context['semester_name'] = semester.name
    return render_to_response('enrollment_by_teacher.html',
                              context_instance=context)


def enrollment_report(request):
    """Provides a list of students enrolled in each class.  This information is
    then used to pay teachers the appropriate amount for each class.
    """
    if request.method == 'GET':
        context = RequestContext(request)
        semesters = Semester.objects.all().order_by('-start_date')
        context['semesters'] = semesters
        return render_to_response('enrollment.html', context_instance=context)
    else:
        if 'by_family' in request.POST:
            return enrollment_by_family(request)
        else:
            return render_enrollment_by_teacher(request)


def get_student(user):
    student = None
    try:
        student = Student.objects.filter(student=user)
    except Student.DoesNotExist:
        pass
    return student


def get_teacher(user):
    teacher = None
    try:
        teacher = Teacher.objects.filter(user=user)
    except Teacher.DoesNotExist:
        pass

    return teacher


@login_required
def student_assignments(request):
    student = get_object_or_404(Student, user=request.user)
    context = RequestContext(request)
    s = {'name': student.student.full_name}
    current = get_active_semester(request)
    s['courses'] = get_courses_for_semester_and_student(current.id,
                                                        student.id)
    context['student'] = s
    context['courses'] = s['courses']

    return render_to_response('student_assignments.html',
                              context_instance=context)


@login_required
def assignments_for_student(request, student_id):
    # Assignments for this student, by course
    context = RequestContext(request)
    student = Student.objects.get(pk=student_id)
    context['name'] = student.student.full_name
    # get courses for this student
    today = date.today()
    enrollments = (Enrollment.objects
                   .filter(course__semester__start_date__lte=today)
                   .filter(course__semester__end_date__gte=today)
                   .filter(drop_date=None)
                   .filter(student=student)
                   .order_by('course__semester__start_date'))
    # for each course get course assignments
    courses = []
    for enr in enrollments:
        course = enr.course
        sa = get_student_assignments(student_id, course)
        if sa:
            courses.append(course)
            course.assignments = sa
    context['courses'] = courses

    return render_to_response('assignments_for_student.html',
                              context_instance=context)


@login_required
def assignments_for_student_and_course(request, student_id,
                                       course_id, unit_id=None):
    context = RequestContext(request)
    student = get_object_or_404(Student, pk=student_id)
    context['student'] = student
    course = get_object_or_404(Course, pk=course_id)
    units = get_student_assignments(student_id, course)
    course.units = units
    context['course'] = course
    context['unit_id'] = unit_id
    context['course_id'] = course_id
    context['student_id'] = student_id

    return render_to_response('assignments_for_student.html',
                              context_instance=context)


@login_required
def edit_student_assignment(request, assignment_id, student_id):
    student = get_object_or_404(Student, pk=student_id)
    assignment = get_object_or_404(StudentAssignment, pk=assignment_id)
    context = RequestContext(request)
    if request.method == 'POST':
        form = StudentAssignmentForm(request.POST, instance=assignment)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect(
                reverse('assignments_for_student_and_course',
                        args=[student.id,
                              assignment.assignment.unit.course.id,
                              assignment.assignment.unit.id]))
    else:
        assignment.turn_in_date = assignment.assignment.due_date
        form = StudentAssignmentForm(instance=assignment)

    context['form'] = form
    context['student'] = student
    return render_to_response('edit_student_assignment.html',
                              context_instance=context)


@login_required
def add_unit_for_course(request, course_id):
    # Add a unit to this course
    course = get_object_or_404(Course, id=course_id)
    context = RequestContext(request)
    if request.method == 'POST':
        form = UnitForm(request.POST, initial={'course': course})
        if form.is_valid():
            unit = form.save(commit=False)
            unit.course = course
            unit.save()
            return HttpResponseRedirect(reverse('manage_assignments',
                                        args=[course_id, unit.id]))
    else:
        form = UnitForm(initial={'course': course})
        context['course_title'] = course.title

    context['form'] = form
    return render_to_response('add_unit.html', context_instance=context)


@login_required
def edit_unit(request, unit_id):
    unit = get_object_or_404(Unit, pk=unit_id)
    context = RequestContext(request)
    if request.method == 'POST':
        form = UnitForm(request.POST, initial={'course': course},
                        instance=unit)
        form.save()
        return HttpResponseRedirect(reverse('manage_assignments',
                                    args=[unit.course_id, unit.id]))
    else:
        form = UnitForm(initial={'course': course}, instance=unit)
        context['course_title'] = unit.course.title

    context['form'] = form
    return render_to_response('edit_unit.html', context_instance=context)


@login_required
def edit_unit_grade(request, unit_id, student_id):
    unit = get_object_or_404(Unit, pk=unit_id)
    student = get_object_or_404(Student, pk=student_id)
    student_unit, created = StudentUnit.objects.get_or_create(unit=unit,
                                                              student=student)
    context = RequestContext(request)
    if request.method == 'POST':
        form = UnitGradeForm(request.POST, instance=student_unit)
        form.save()
        return HttpResponseRedirect(
            reverse('assignments_for_student_and_course',
                    args=[student_id, unit.course_id, unit_id]))
    else:
        form = UnitGradeForm(instance=student_unit)

    context['form'] = form
    context['student'] = student
    context['unit'] = unit
    return render_to_response('edit_unit_grade.html', context_instance=context)


@login_required
def add_assignment_for_unit(request, unit_id):
    # Add a course 'template' to a course unit
    context = RequestContext(request)
    unit = get_object_or_404(Unit, pk=unit_id)
    if request.method == 'POST':
        form = AssignmentForm(request.POST)
        if form.is_valid():
            assignment = form.save(commit=False)
            assignment.unit = unit
            assignment.save()
            return HttpResponseRedirect(reverse('manage_assignments',
                                        args=[unit.course.id, unit_id]))
    else:
        form = AssignmentForm(initial={'unit': unit})
        context['course_title'] = unit.course.title

    context['form'] = form
    return render_to_response('add_assignment.html', context_instance=context)


@login_required
def edit_assignment(request, assignment_id):
    assignment = get_object_or_404(Assignment, pk=assignment_id)
    context = RequestContext(request)
    if request.method == 'POST':
        form = AssignmentForm(request.POST, instance=assignment)
        if form.is_valid():
            assignment = form.save()
            return HttpResponseRedirect(
                reverse('manage_assignments', args=[assignment.unit.course.id,
                                                    assignment.unit.id]))
    else:
        form = AssignmentForm(instance=assignment)
        context['course_title'] = assignment.unit.course.title

    context['form'] = form
    return render_to_response('edit_assignment.html', context_instance=context)


@login_required
def delete_assignment(request, assignment_id):
    # Make sure the person doing this is the teacher for the course or an admin
    assignment = get_object_or_404(Assignment, pk=assignment_id)
    user = request.user
    may_edit = False
    if user.is_staff or user.is_superuser:
        may_edit = True
    if not may_edit:
        try:
            teacher = Teacher.objects.get(user=user)
            if teacher in assignment.unit.course.teachers.all():
                may_edit = True
        except Teacher.DoesNotExist:
            return HttpResponseNotFound()
    if may_edit:
        assignment.delete()
    return HttpResponseRedirect(reverse('manage_assignments',
                                        args=[assignment.unit.course.id,
                                              assignment.unit.id]))


@login_required
def delete_unit(request, unit_id):
    unit = get_object_or_404(Unit, pk=unit_id)
    user = request.user
    may_edit = False
    if user.is_staff or user.is_superuser:
        may_edit = True
    if not may_edit:
        try:
            teacher = Teacher.objects.get(user=user)
            if teacher in unit.course.teachers.all():
                may_edit = True
        except Teacher.DoesNotExist:
            return HttpResponseNotFound()
    if may_edit:
        unit.delete()
    return HttpResponseRedirect(reverse('manage_assignments',
                                        args=[unit.course.id, unit_id]))


@login_required
def manage_assignments(request, edited_course=None, edited_unit=None):
    # Manage assignment templates sorted by course
    context = RequestContext(request)
    user = request.user
    teacher = get_object_or_404(Teacher, user=user)
    t = {'name': teacher.contact_info.full_name}
    current = get_active_semester(request)
    courses = []
    semester_courses = get_assignment_templates(teacher, current.id)
    if len(semester_courses) > 0:
        courses.extend(semester_courses)
    context['teacher'] = t
    context['courses'] = courses
    context['edited_course'] = edited_course
    context['edited_unit'] = edited_unit

    return render_to_response('manage_assignments.html',
                              context_instance=context)


def get_assignment_templates(teacher, semester_id):
    # get the courses by semester_id
    # for each course get the course assignments by unit
    # return a list of courses with attached assignment templates
    courses = (Course.objects
               .filter(teachers=teacher)
               .filter(semester__id=semester_id)
               .order_by('title'))
    if courses:
        for course in courses:
            units = Unit.objects.filter(course=course).order_by('date')
            course.units = []
            for unit in units:
                assignments = (Assignment.objects.filter(unit=unit)
                               .order_by('due_date', 'name').values())
                unit.assignments = assignments
                course.units.append(unit)
    return courses


@login_required
def assignments_by_course(request, selected_course=None):
    # A teacher's assignments sorted by course
    context = RequestContext(request)
    user = request.user
    teacher = get_object_or_404(Teacher, user=user)
    t = {'name': teacher.contact_info.full_name}
    current = get_active_semester(request)
    result = enrollment_for_teacher(teacher, current.id)
    if result:
        enroll_dict = result[0]
        t['courses'] = enroll_dict['courses']
    context['teacher'] = t
    context['selected_course'] = selected_course

    return render_to_response('assignments_by_course.html',
                              context_instance=context)


@login_required
def assignments_for_course(request, course_id=None):
    context = RequestContext(request)
    course = Course.objects.get(pk=course_id)
    context['name'] = course.title
    # get the course assignments for this course
    course_assignments = (Assignment.objects.filter(course=course)
                          .order_by('due_date'))
    if len(course_assignments):
        # get all students enrolled in this course
        today = date.today()
        enrollments = (Enrollment.objects
                       .filter(course__semester__start_date__lte=today)
                       .filter(course__semester__end_date__gte=today)
                       .filter(drop_date=None)
                       .filter(course=course)
                       .order_by('student__student__last_name')
                       .order_by('student__student__first_name'))
        students = []
        # for each student
        for enr in enrollments:
            student = enr.student
            students.append(student)
            student.student_assignments = []
            for ca in course_assignments:
                sa = (StudentAssignment.objects
                      .filter(student=student)
                      .filter(assignment=ca).order_by('assignment__due_date'))
                if len(sa) > 0:
                    sa = sa[0]
                else:
                    sa = StudentAssignment(student=student, assignment=ca)
                    sa.save()
                form = StudentAssignmentForm(instance=sa)
                student.student_assignments.append(form)
        context['students'] = students
    return render_to_response('assignments_for_course.html',
                              context_instance=context)


@login_required
def copy_assignments_for_unit(request, unit_id):
    context = RequestContext(request)
    unit = get_object_or_404(Unit, pk=unit_id)
    teacher = get_object_or_404(Teacher, user=request.user)
    if request.method == 'POST':
        form = CopyAssignmentsForm(unit, teacher, request.POST)
        if form.is_valid():
            days_delta = form.cleaned_data['days_delta']
            # copy all of the assignments to the new course
            destination_unit = destination_unit = Unit()
            destination_unit.course = unit.course
            destination_unit.name = form.cleaned_data['new_unit_name']
            destination_unit.date = unit.date + timedelta(days=days_delta)
            destination_unit.save()
            assignments = Assignment.objects.filter(unit=unit)
            for assignment in assignments:
                copy = Assignment()
                copy.unit = destination_unit
                copy.due_date = (assignment.due_date +
                                 timedelta(days=days_delta))
                copy.instructions = assignment.instructions
                copy.name = assignment.name
                copy.weight = assignment.weight
                copy.save()
            return HttpResponseRedirect(reverse('manage_assignments',
                                        args=[unit.course.id,
                                              destination_unit.id]))
    else:
        form = CopyAssignmentsForm(unit, teacher)
        context['unit'] = unit

    context['form'] = form
    return render_to_response('copy_assignments_for_unit.html',
                              context_instance=context)


@login_required
def change_unit_assignment_dates(request, unit_id):
    context = RequestContext(request)
    unit = get_object_or_404(Unit, pk=unit_id)
    teacher = get_object_or_404(Teacher, user=request.user)
    if request.method == 'POST':
        form = ChangeUnitAssignmentDatesForm(unit, teacher, request.POST)
        if form.is_valid():
            days_delta = form.cleaned_data['days_delta']
            assignments = Assignment.objects.filter(unit=unit)
            for assignment in assignments:
                assignment.due_date = (assignment.due_date +
                                       timedelta(days=days_delta))
                assignment.save()
            unit.date = unit.date + timedelta(days=days_delta)
            unit.save()
            return HttpResponseRedirect(reverse('manage_assignments',
                                        args=[unit.course.id,
                                              unit.id]))
    else:
        form = ChangeUnitAssignmentDatesForm(unit, teacher)
        context['unit'] = unit

    context['form'] = form
    return render_to_response('change_unit_assignment_dates.html',
                              context_instance=context)


@login_required
def assignment_info(request, assignment_id):
    sa = get_object_or_404(StudentAssignment, pk=assignment_id)
    return HttpResponse(sa.assignment.instructions)


@login_required
def teacher_send_message(request, selected_course=None):
    context = RequestContext(request)
    user = request.user
    teacher = get_object_or_404(Teacher, user=user)
    if request.method == 'POST':
        form = EmailForm([], True, request.POST)
        if form.is_valid():
            to = []
            recipients = []
            msg = form.cleaned_data['body']
            subject = form.cleaned_data['subject']
            email_from = teacher.email
            group_id = uuid.uuid4()
            ids = form.cleaned_data['recipient_id']
            cc_parents = bool(form.cleaned_data['include_parents'])
            for id in ids:
                student = Student.objects.get(pk=id)
                to.append(student.student.email)
                recipients.append(student.user)
                if cc_parents:
                    to.append(student.family.mother.email or
                              student.family.father.email)
                    recipients.append(student.family.user)
            try:
                send_mail(subject, msg, email_from, to,
                          fail_silently=False)
                now = datetime.now()
                for recipient in recipients:
                    message = Message()
                    message.email_group_id = group_id
                    message.subject = subject
                    message.body = msg
                    message.date = now
                    message.sender = user
                    message.recipient = recipient
                    message.save()
            except smtplib.SMTPException, e:
                print e

            extra = {}
            extra['to'] = to
            extra['subject'] = subject
            return redirect('/messages_sent/%s' % group_id,
                            extra_context=extra)
        else:
            context['form'] = form
            context['selected_course'] = selected_course
    current = get_active_semester(request)
    result = enrollment_for_teacher(teacher, current.id)
    if result:
        enroll_dict = result[0]
        courses = enroll_dict['courses']
        for course in courses:
            # The if part is used when validation fails and we need to display
            # the validation error message correctly
            frm = EmailForm(course['students'])
            if selected_course and int(selected_course) == course['id']:
                form.fields['recipient_id'].choices = \
                    frm.fields['recipient_id'].choices
                course['form'] = form
            else:
                course['form'] = frm
        context['courses'] = courses

    return render_to_response('messages.html', context_instance=context)


@login_required
def student_send_message(request, selected_course=None):
    context = RequestContext(request)
    user = request.user
    student = get_object_or_404(Student, user=user)
    if request.method == 'POST':
        form = EmailForm([], False, request.POST)
        if form.is_valid():
            to = []
            recipients = []
            msg = form.cleaned_data['body']
            subject = form.cleaned_data['subject']
            email_from = student.email
            group_id = uuid.uuid4()
            ids = form.cleaned_data['recipient_id']
            for id in ids:
                teacher = Teacher.objects.get(pk=id)
                to.append(teacher.email)
                recipients.append(teacher.user)
            try:
                send_mail(subject, msg, email_from, to,
                          fail_silently=False)
                now = datetime.now()
                for recipient in recipients:
                    message = Message()
                    message.email_group_id = group_id
                    message.subject = subject
                    message.body = msg
                    message.date = now
                    message.sender = user
                    message.recipient = recipient
                    message.save()
            except smtplib.SMTPException, e:
                print e.message

            extra = {}
            extra['to'] = to
            extra['subject'] = subject
            return redirect('/messages_sent/%s' % group_id,
                            extra_context=extra)
        else:
            context['form'] = form
            context['selected_course'] = selected_course
    current = get_active_semester(request)
    courses = get_courses_for_semester_and_student(current.id, student.id,
                                                   get_assignments=False)
    course_list = []
    if courses:
        for course in courses:
            # The if part is used when validation fails and we need to display
            # the validation error message correctly
            d = {'title': course.title, 'id': course.id}
            frm = EmailForm(course.teachers.all(), show_cc=False)
            if selected_course and int(selected_course) == course.id:
                form.fields['recipient_id'].choices = \
                    frm.fields['recipient_id'].choices
                d['form'] = form
            else:
                d['form'] = frm
            course_list.append(d)
        context['courses'] = course_list

    return render_to_response('messages.html', context_instance=context)


@login_required
def message_history(request):
    context = RequestContext(request)
    user = request.user
    messages = Message.objects.filter(sender=user).order_by('email_group_id')
    msgs_from = []
    id = None
    group = None
    for msg in messages:
        if msg.email_group_id != id:
            # start a new group
            id = msg.email_group_id
            group = {}
            group['recipients'] = [msg.recipient]
            group['subject'] = msg.subject
            group['body'] = msg.body
            group['date'] = msg.date
            msgs_from.append(group)
        else:
            # append to existing group
            group['recipients'].append(msg.recipient)
    context['messages_from'] = msgs_from

    msgs_to = Message.objects.filter(recipient=user).order_by('date')
    context['messages_to'] = msgs_to
    return render_to_response('message_history.html', context_instance=context)


@login_required
def messages_sent(request, group_id):
    context = RequestContext(request)
    messages = Message.objects.filter(email_group_id=group_id)
    if messages.count() > 0:
        context['subject'] = messages[0].subject
        recipients = [msg.recipient for msg in messages]
        context['recipients'] = ['%s %s - %s' % (x.first_name, x.last_name,
                                                 x.email) for x in recipients]
    return render_to_response('messages_sent.html',
                              context_instance=context)


@login_required
def grades_matrix(request):
    # TODO: Need to speed this up
    # or
    # break it up by course so this is only done for one course at a time
    context = RequestContext(request)
    user = request.user
    teacher = get_object_or_404(Teacher, user=user)
    current = get_active_semester(request)
    result = enrollment_for_teacher(teacher, current.id)
    if result:
        enroll_dict = result[0]
        courses = enroll_dict['courses']
        for course in courses:
            units = (Unit.objects.filter(course__id=course['id'])
                     .order_by('date'))
            course['units'] = units
            for unit in units:
                cas = (Assignment.objects.filter(unit=unit)
                       .order_by('due_date'))
                unit.assignments = cas
                unit.rows = []
                for student in course['students']:
                    row = [student.student.full_name]
                    unit.rows.append(row)
                    for ca in cas:
                        sa = get_or_create_assignment_no_dups(student.id, ca)
                        row.append(sa.grade)
                    unit_grade = (StudentUnit.objects
                                  .filter(unit=unit)
                                  .filter(student=student))
                    if unit_grade:
                        row.append(unit_grade[0].grade)
                    else:
                        row.append(None)

    context['courses'] = courses

    return render_to_response('grades_matrix.html',
                              context_instance=context)


@login_required
def calendar(request, year=None, month=None):
    context = RequestContext(request)
    if not year:
        today = date.today()
        year = today.year
        month = today.month
    student = get_object_or_404(Student, user=request.user)
    assignments = get_calendar_assignments(request, student.id, year, month)
    cal = AssignmentCalendar(6, assignments).formatmonth(year, month)
    return render_to_response('student_assignments_calendar.html',
                              {'calendar': mark_safe(cal)},
                              context_instance=context)


@login_required
def edit_family(request):
    family = get_object_or_404(Family, user=request.user)
    context = RequestContext(request)
    if request.method == 'POST':
        family_form = FamilyForm(request.POST, instance=family)
        address_form = AddressForm(request.POST, instance=family.address)
        mother_form = ContactInfoForm(request.POST, instance=family.mother)
        father_form = ContactInfoForm(request.POST, instance=family.father)

        if (family_form.is_valid() and mother_form.is_valid()
                and father_form.is_valid()):
            family = family_form.save()
            family.mother = mother_form.save()
            family.father = father_form.save()
            family.address = address_form.save()
            family.mother.save()
            family.father.save()
            family.address.save()
            family.save()
            return HttpResponseRedirect(
                reverse('edit_family'))
    else:
        family_form = FamilyForm(instance=family)
        mother_form = MotherForm(instance=family.mother)
        father_form = FatherForm(instance=family.father)
        address_form = AddressForm(instance=family.address)
    context['family_form'] = family_form
    context['mother_form'] = mother_form
    context['father_form'] = father_form
    context['address_form'] = address_form
    return render_to_response('edit_family.html', context_instance=context)


@login_required
def add_student(request):
    context = RequestContext(request)
    family = get_object_or_404(Family, user=request.user)
    if request.method == 'POST':
        user_form = UserForm(request.POST)
        student_form = StudentForm(request.POST)
        contact_info_form = ContactInfoForm(request.POST)
        if (user_form.is_valid() and student_form.is_valid()
                and contact_info_form.is_valid()):
            user = UserForm.save()
            student = StudentForm.save()
            student.user = user
            student.student = contact_info_form()
            family.student_set.add(student)
            user.save()
            student.student.save()
            student.save()
            return HttpResponseRedirect(reverse('edit_family'))
    else:
        context['user_form'] = UserForm()
        context['student_form'] = StudentForm()
        context['contact_info_form'] = ContactInfoForm()
        return render_to_response('add_studcent.html',
                                  context_instance=context)


@login_required
def delete_student(request, student_id):
    student = Student.objects.get(pk=student_id)
    context = RequestContext(request)
    if request.method == 'POST':
        # if student is enrolled in a class already
        # don't delete
        enrs = Enrollment.objects.get(student=student)
        if enrs:
            context['error'] = 'Student can not be deleted'
        else:
            student.delete()

    return render_to_response('edit_family.html', context_instance=context)


@login_required
def edit_student(request):
    pass


if __name__ == '__main__':
    _get_attendance_info(None)
