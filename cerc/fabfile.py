from fabric.api import local


def manage(command, *args):
    """Run manage.py command"""
    local("virtualenv/bin/python manage.py {0} {1}".format(
        command, " ".join(args)), capture=False,)


def runserver(port=8000):
    manage("runserver", str(port))


def syncdb():
    manage("syncdb", "--migrate")


def run(port=8000):
    syncdb()
    runserver(port)
