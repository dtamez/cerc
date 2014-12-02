'''
Created on Aug 2, 2009

@author: dtamez
'''
from datetime import datetime

from django.contrib import admin
from django.shortcuts import render_to_response
from django.template import RequestContext

from cerc.models import (
    Address,
    Assignment,
    Attendance,
    ContactInfo,
    Conduct,
    Course,
    Enrollment,
    Family,
    Message,
    Teacher,
    Student,
    StudentAssignment,
    Semester,
    TeacherRequest,
)


class CourseAdmin(admin.ModelAdmin):
    list_filter = ('approved', 'semester', 'teachers')
    actions = ['clone_for_next_semester']
    search_fields = ('title',)

    def clone_for_next_semester(modelAdmin, request, queryset):
        if request.POST.get('post'):
            n = queryset.count()
            if n:
                for obj in queryset:
                    clone = Course()
                    semester = (Semester.objects
                                .get(pk=request.POST['semester']))
                    clone.semester = semester
                    clone.title = obj.title
                    clone.description = obj.description
                    clone.code = obj.code
                    clone.day = obj.day
                    clone.time = obj.time
                    clone.tuition = obj.tuition
                    clone.min_slots = obj.min_slots
                    clone.max_slots = obj.max_slots
                    clone.length = obj.length
                    clone.days_per_week = obj.days_per_week
                    clone.materials_fee = obj.materials_fee
                    clone.materials_list = obj.materials_list
                    clone.age_level = obj.age_level
                    clone.grade_level = obj.grade_level
                    clone.homework_hours = obj.homework_hours
                    clone.first_time_choice = obj.first_time_choice
                    clone.second_time_choice = obj.second_time_choice
                    clone.third_time_choice = obj.third_time_choice
                    clone.schedule_considerations = obj.schedule_considerations
                    clone.approved = True
                    clone.save()
                    clone.teachers = obj.teachers.all()
                    clone.save()

                    for student in obj.students.all():
                        enrollment = Enrollment()
                        enrollment.course = clone
                        enrollment.student = student
                        enrollment.entroll_date = datetime.today()
                        enrollment.save()

            modelAdmin.message_user(request,
                                    'Number of courses cloned: %d' % n)
            return None

        # Display the intermediate page to get start and end dates
        semesters = Semester.objects.all().order_by('-start_date')
        context = {
            "cloneable_objects": queryset,
            "semesters": semesters,
        }
        return render_to_response('clone_course.html', context,
                                  context_instance=RequestContext(request))

    clone_for_next_semester.short_description = "Clone for next semester"


class EnrollmentAdmin(admin.ModelAdmin):
    search_fields = ('course__title', )
    list_filter = ('course__semester__name', 'course')
    ordering = ['course']


class StudentAdmin(admin.ModelAdmin):
    search_fields = ('user__username', 'user__first_name', 'user__last_name')
    raw_id_fields = ['user']


class FamilyAdmin(admin.ModelAdmin):
    search_fields = ('family_name', 'mother__first_name', 'mother__last_name',
                     'father__first_name', 'father__last_name')
    raw_id_fields = ['user']


class TeacherAdmin(admin.ModelAdmin):
    search_fields = ('user__username', 'user__first_name', 'user__last_name')
    raw_id_fields = ['user']

admin.site.register(Address)
admin.site.register(Assignment)
admin.site.register(Attendance)
admin.site.register(ContactInfo)
admin.site.register(Conduct)
admin.site.register(Course, CourseAdmin)
admin.site.register(Enrollment, EnrollmentAdmin)
admin.site.register(Family, FamilyAdmin)
admin.site.register(Message)
admin.site.register(Semester)
admin.site.register(Student, StudentAdmin)
admin.site.register(StudentAssignment)
admin.site.register(Teacher, TeacherAdmin)
admin.site.register(TeacherRequest)
