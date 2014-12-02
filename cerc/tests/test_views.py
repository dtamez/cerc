#! /usr/bin/env python
# -*- coding: utf-8 -*-
# vim:fenc=utf-8
#
# Copyright © 2014 Danny Tamez <zematynnad@gmail.com>
#
# Distributed under terms of the MIT license.

"""
Unit tests for cerc.views
"""
from django.test import (
    TestCase,
)

from cerc.tests.factory import (
    ModelFactory,
    PSWD,
)


factory = ModelFactory()


class TestViews(TestCase):

    fixtures = ['groups.yaml']

    def test_index_teacher(self):
        u = factory.make_teacher()
        self.client.login(username=u.user.username,
                          password=PSWD)

        resp = self.client.get('/', follow=True)

        self.assertContains(resp, 'Submit a New Course')
        expected = {'name': u.full_name}
        self.assertEqual(resp.context['teacher'], expected)
        self.assertTemplateUsed(resp, 'index_teacher.html')

    def test_index_student(self):
        u = factory.make_student()
        self.client.login(username=u.user.username,
                          password=PSWD)

        resp = self.client.get('/', follow=True)

        self.assertContains(resp, 'student_send_message')
        expected = {'name': u.full_name}
        self.assertEqual(resp.context['student'], expected)
        self.assertTemplateUsed(resp, 'index_student.html')

    def test_index_family(self):
        u = factory.make_family()
        self.client.login(username=u.user.username,
                          password=PSWD)

        resp = self.client.get('/', follow=True)

        self.assertContains(resp, 'Family Approval Forms')
        self.assertTemplateUsed(resp, 'index_family.html')

    def test_index_staff(self):
        u = factory.make_user(is_staff=True)
        self.client.login(username=u.username,
                          password=PSWD)

        resp = self.client.get('/', follow=True)

        self.assertContains(resp, 'Site administration')

    def test_upcoming_courses_none(self):
        u = factory.make_teacher()
        self.client.login(username=u.user.username,
                          password=PSWD)

        resp = self.client.get('/upcoming_courses/')

        self.assertNotIn('upcoming', resp.context['teacher'])

    def test_upcoming_courses_two(self):
        u = factory.make_teacher()
        s = factory.make_semester()
        factory.make_course(semester=s, teacher=u)
        factory.make_course(semester=s, teacher=u)
        self.client.login(username=u.user.username,
                          password=PSWD)

        resp = self.client.get('/upcoming_courses/')

        self.assertIn('upcoming', resp.context['teacher'])
        courses = resp.context['teacher'].get('upcoming')
        self.assertEqual(2, len(courses))

    def test_upcoming_courses_one_and_one(self):
        u = factory.make_teacher()
        u2 = factory.make_teacher()
        s = factory.make_semester()
        course = factory.make_course(semester=s, teacher=u)
        factory.make_course(semester=s, teacher=u2)
        self.client.login(username=u.user.username,
                          password=PSWD)

        resp = self.client.get('/upcoming_courses/')

        self.assertIn('upcoming', resp.context['teacher'])
        courses = resp.context['teacher'].get('upcoming')
        self.assertEqual(1, len(courses))
        self.assertEqual(course, courses[0])

    def test_current_courses(self):
        pass
