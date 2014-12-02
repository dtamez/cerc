import os


PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__),
                                            os.pardir))
PACKAGE_ROOT = os.path.abspath(os.path.dirname(__file__))

ALLOWED_HOSTS = ['enroll-cerconline.org',
                 'www.enroll-cerconline.org',
                 'localhost']

ADMINS = [
    ("Danny Tamez", "zematynnad@gmail.com"),
]

MANAGERS = ADMINS

TIME_ZONE = "America/Chicago"
LANGUAGE_CODE = "en-us"

SITE_ID = int(os.environ.get("SITE_ID", 1))

USE_I18N = True
USE_L10N = True
USE_TZ = True

STATIC_ROOT = "/home/enrollmgr/webapps/cerc_static/"
STATIC_URL = "/static/"
STATICFILES_DIRS = [
    os.path.join(PACKAGE_ROOT, "static"),
]

# List of finder classes that know how to find static files in
# various locations.
STATICFILES_FINDERS = [
    "django.contrib.staticfiles.finders.FileSystemFinder",
    "django.contrib.staticfiles.finders.AppDirectoriesFinder",
]

SECRET_KEY = 'y!v#8(u2@8vxs%snov1(orujd+^ff-*rymnmfw=or5c&xh-(em'

# Application definition
TEMPLATE_LOADERS = [
    "django.template.loaders.filesystem.Loader",
    "django.template.loaders.app_directories.Loader",
]

TEMPLATE_CONTEXT_PROCESSORS = [
    "django.contrib.auth.context_processors.auth",
    "django.core.context_processors.debug",
    'cerc.context_processors.semesters',
    'cerc.context_processors.users',
    "django.core.context_processors.i18n",
    "django.core.context_processors.media",
    "django.core.context_processors.static",
    "django.core.context_processors.tz",
    "django.core.context_processors.request",
    "django.contrib.messages.context_processors.messages",
]

MIDDLEWARE_CLASSES = [
    "django.middleware.common.CommonMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
]

ROOT_URLCONF = 'cerc.urls'
WSGI_APPLICATION = 'cerc.wsgi.application'

TEMPLATE_DIRS = [os.path.join(PACKAGE_ROOT, 'templates')]
CRISPY_TEMPLATE_PACK = 'uni_form'

INSTALLED_APPS = (
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'eventlog',
    'crispy_forms',
    'registration',
    'django_ajax',
    'south',
    'cerc',
)
AUTH_PROFILE_MODULE = 'cerc.models.Family'
ACCOUNT_ACTIVATION_DAYS = 2
DEFAULT_FROM_EMAIL = 'administrator@enroll-cerconline.org'
LOGIN_REDIRECT_URL = '/'

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "filters": {
        "require_debug_false": {
            "()": "django.utils.log.RequireDebugFalse"
        }
    },
    "handlers": {
        "mail_admins": {
            "level": "ERROR",
            "filters": ["require_debug_false"],
            "class": "django.utils.log.AdminEmailHandler"
        }
    },
    "loggers": {
        "django.request": {
            "handlers": ["mail_admins"],
            "level": "ERROR",
            "propagate": True,
        },
    }
}


EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'

DEFAULT_FROM_EMAIL = 'administrator@enroll-cerconline.org'

try:
    from local_settings import *
except ImportError:
    pass
