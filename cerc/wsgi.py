import os
import sys

sys.path.append('/home/enrollmgr/lib/python2.7')

os.environ['DJANGO_SETTINGS_MODULE'] = 'cerc.settings'

from django.core.handlers.wsgi import WSGIHandler

application = WSGIHandler()
