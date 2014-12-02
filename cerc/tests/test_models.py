#! /usr/bin/env python
# -*- coding: utf-8 -*-
# vim:fenc=utf-8
#
# Copyright © 2014 Danny Tamez <zematynnad@gmail.com>
#
# Distributed under terms of the MIT license.

"""
Unit tests for cerc.models
"""
import datetime

from django.contrib.auth.models import Group


from django.test import TestCase


from cerc.tests.factory import ModelFactory


class TestModels(TestCase):
    fixtures = ['groups.yaml']

    model_factory = ModelFactory()

    def test_create_family_adds_to_group(self):
        prev = Group.objects.get(name='Families').user_set.count()

        TestModels.model_factory.make_family()

        current = Group.objects.get(name='Families').user_set.count()
        self.assertEqual(prev + 1, current)

    def test_create_teacher_adds_to_group(self):
        prev = Group.objects.get(name='Teachers').user_set.count()

        TestModels.model_factory.make_teacher()

        current = Group.objects.get(name='Teachers').user_set.count()
        self.assertEqual(prev + 1, current)

    def test_create_student_adds_to_group(self):
        prev = Group.objects.get(name='Students').user_set.count()

        TestModels.model_factory.make_student()

        current = Group.objects.get(name='Students').user_set.count()
        self.assertEqual(prev + 1, current)

    def test_enrollment_is_active_true(self):
        today = datetime.date.today()
        start_date = today - datetime.timedelta(days=1)
        end_date = today + datetime.timedelta(days=1)
        semester = TestModels.model_factory.make_semester(
            start_date=start_date, end_date=end_date)
        course = TestModels.model_factory.make_course(semester=semester)
        dct = {'drop_date': None, 'course': course}

        enrollment = TestModels.model_factory.make_enrollment(**dct)

        self.assertTrue(enrollment.is_active())

    def test_enrollment_is_active_false(self):
        today = datetime.date.today()
        start_date = today - datetime.timedelta(days=11)
        end_date = today - datetime.timedelta(days=1)
        semester = TestModels.model_factory.make_semester(
            start_date=start_date, end_date=end_date)
        course = TestModels.model_factory.make_course(semester=semester)
        dct = {'drop_date': None, 'course': course}

        enrollment = TestModels.model_factory.make_enrollment(**dct)

        self.assertFalse(enrollment.is_active())

    def test_enrollment_is_active_false_dropped(self):
        today = datetime.date.today()
        start_date = today - datetime.timedelta(days=1)
        end_date = today + datetime.timedelta(days=1)
        semester = TestModels.model_factory.make_semester(
            start_date=start_date, end_date=end_date)
        course = TestModels.model_factory.make_course(semester=semester)
        dct = {'drop_date': today, 'course': course}

        enrollment = TestModels.model_factory.make_enrollment(**dct)

        self.assertFalse(enrollment.is_active())
