#! /usr/bin/env python
# -*- coding: utf-8 -*-
# vim:fenc=utf-8
#
# Copyright © 2014 Danny Tamez <zematynnad@gmail.com>
#
# Distributed under terms of the MIT license.

"""
Factory for creating models for tests
"""
import datetime
import random
import string

from django.contrib.auth.models import (
    User,
)

from cerc.models import (
    Address,
    ContactInfo,
    Course,
    Enrollment,
    Family,
    Semester,
    Student,
    Teacher,
)

PSWD = 'password'


def get_random(prefix='', len=10):
    rnd = ''.join(random.choice(string.ascii_letters) for _ in range(len))
    return prefix + rnd


def get_random_email():
    name = get_random(len=5)
    domain = get_random(len=5)
    return '{}@{}.com'.format(name, domain)


class ModelFactory(object):

    def make_user(self, first_name=None, last_name=None,
                  email=None, **kwargs):
        first_name = first_name or get_random('first_name')
        last_name = last_name or get_random('lastname')
        username = get_random()
        email = email or get_random_email()
        user = User.objects.create_user(username=username, email=email,
                                        password=PSWD)
        user.is_active = True
        for k, v in kwargs.iteritems():
            setattr(user, k, v)
        user.save()
        return user

    def make_contact_info(self, first_name=None, last_name=None, email=None,
                          phone=None, **kwargs):
        info = ContactInfo()
        info.first_name = first_name or get_random('first_name')
        info.last_name = last_name or get_random('last_name')
        info.email = email or get_random_email()
        for k, v in kwargs.iteritems():
            setattr(info, k, v)
        info.save()
        return info

    def make_address(self, street=None, **kwargs):
        addr = Address()
        addr.street = street or get_random('street')
        for k, v in kwargs:
            setattr(addr, k, v)
        addr.save()
        return addr

    def make_family(self, **kwargs):
        fam = Family()
        last_name = get_random('last')
        for k, v in kwargs.iteritems():
            setattr(fam, k, v)
        fam.user = (fam.user if fam.user_id else
                    self.make_user(last_name=last_name))
        fam.father = (fam.father if fam.father_id else
                      self.make_contact_info(last_name=last_name))
        fam.mother = (fam.mother if fam.mother_id else
                      self.make_contact_info(last_name=last_name))
        fam.save()
        return fam

    def make_teacher(self, **kwargs):
        t = Teacher()
        for k, v in kwargs.iteritems():
            setattr(t, k, v)
        t.user = (t.user if t.user_id else
                  self.make_user())
        t.address = t.address if t.address_id else self.make_address()
        t.contact_info = (t.contact_info if t.contact_info_id else
                          self.make_contact_info())
        t.save()
        return t

    def make_student(self, **kwargs):
        fam = self.make_family()
        last_name = fam.user.last_name
        student = Student()
        student.family = fam
        for k, v in kwargs.iteritems():
            setattr(student, k, v)

        student.user = (student.user if student.user_id else
                        self.make_user(last_name=last_name))
        student.student = (student.student if student.student_id else
                           self.make_contact_info(last_name=last_name))
        student.save()
        return student

    def make_semester(self, **kwargs):
        sem = Semester()
        sem.name = kwargs.get('name', get_random(len=5))
        sem.start_date = kwargs.get('start_date',  datetime.date.today())
        sem.end_date = kwargs.get('end_date', datetime.date.today())
        sem.save()
        return sem

    def make_course(self, **kwargs):
        course = Course()
        course.title = get_random('title')
        course.description = get_random('desc')
        course.semester = kwargs.get('semester', None) or self.make_semester()
        course.homework_hours = (kwargs.get('homework_hours', None) or
                                 random.choice(range(5)))
        course.max_slots = 5
        course.length = 1.0
        course.materials_fee = 5.0
        course.materials_list = ''
        course.age_level = '14 - 15'
        course.grade_level = '9'
        course.code = get_random(len=4)
        course.save()
        course.teachers.add(kwargs.get('teacher', self.make_teacher()))
        course.save()
        return course

    def make_enrollment(self, **kwargs):
        enroll = Enrollment()
        enroll.drop_date = kwargs.get('drop_date', None)
        enroll.course = kwargs.get('course', None) or self.make_course()
        enroll.student = kwargs.get('student', None) or self.make_student()
        enroll.entroll_date = (kwargs.get('enroll_date', None) or
                               datetime.date.today())
        enroll.save()
        return enroll
