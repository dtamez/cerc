#! /usr/bin/env python
# -*- coding: utf-8 -*-
# vim:fenc=utf-8
#
# Copyright © 2014 Danny Tamez <zematynnad@gmail.com>
#
# Distributed under terms of the MIT license.

"""
Check all python files for pep8 conformance.
"""
import os
import pep8

from collections import defaultdict
from unittest import TestCase

import cerc


class PackagePep8TestCase(TestCase):
    maxDiff = None
    packages = []
    exclude = ['migrations', 'fkfilter.py']

    def setUp(self):
        self.pep8style = pep8.StyleGuide(
            counters=defaultdict(int),
            doctest='',
            exclude=self.exclude,
            filename=['*.py'],
            ignore=[],
            repeat=True,
            select=[],
            show_pep8=False,
            show_source=False,
            max_line_length=79,
            quiet=0,
            statistics=False,
            testsuite='',
            verbose=0,
        )

    def test_all_code(self):
        for package in self.packages:
            self.pep8style.input_dir(os.path.dirname(package.__file__))
        self.assertEqual(self.pep8style.options.report.total_errors, 0)


class CercPep8TestCase(PackagePep8TestCase):
    packages = [cerc]
