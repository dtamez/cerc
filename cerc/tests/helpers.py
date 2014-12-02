#! /usr/bin/env python
# -*- coding: utf-8 -*-
# vim:fenc=utf-8
#
# Copyright © 2014 Danny Tamez <zematynnad@gmail.com>
#
# Distributed under terms of the MIT license.

"""
Utilities and helpful methods for testing.
"""

from contextlib import contextmanager

from django.conf import settings


# Original snippet from http://djangosnippets.org/snippets/2156/
class SettingDoesNotExist:
    pass


def switch_settings(**kwargs):
    """Helper method that updates settings and returns old settings."""
    old_settings = {}
    for key, new_value in kwargs.items():
        old_value = getattr(settings, key, SettingDoesNotExist)
        old_settings[key] = old_value

        if new_value is SettingDoesNotExist:
            delattr(settings, key)
        else:
            setattr(settings, key, new_value)

    return old_settings


@contextmanager
def patch_settings(**kwargs):
    old_settings = switch_settings(**kwargs)
    yield
    switch_settings(**old_settings)


@contextmanager
def disable_csrf(**kwargs):
    middleware_classes = settings.MIDDLEWARE_CLASSES
    settings.MIDDLEWARE_CLASSES = [x for x in middleware_classes
                                   if 'csrt' not in x.lower()]
