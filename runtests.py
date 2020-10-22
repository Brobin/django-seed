#!/usr/bin/env python
import sys
import django
from django.conf import settings
from django.test.utils import get_runner
import sys
from collections import defaultdict


def configure(databases):
    from faker import Faker
    fake = Faker()

    settings.configure(
        DATABASES=databases,
        INSTALLED_APPS=(
            'django_seed',
            'django_nose',
        ),
        TEST_RUNNER = 'django_nose.NoseTestSuiteRunner',
        NOSE_ARGS = [
            '--with-coverage',
            '--cover-package=django_seed',
        ],
        SITE_ID=1,
        SECRET_KEY=fake.sha1(),
    )


if not settings.configured:
    argv = sys.argv[1:]

    args=defaultdict(list)
    for k, v in ((k.lstrip('-'), v) for k,v in (a.split('=') for a in sys.argv[1:])):
        args[k].append(v)

    # Remove all args that are already 
    sys.argv = list(filter(lambda arg: any(arg_name.startswith(arg) for arg_name in [
        '--database'
    ]), sys.argv))

    databases = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': ':memory:',
        }
    }

    # Used for tests in Github Actions
    # Refer to .github/workflows/test.yml to see the Postgres service that is
    # being hosted
    if 'postgres' in args['database']:
        databases['default'] = {
            'ENGINE': 'django.db.backends.postgresql_psycopg2',
            'NAME': 'dbtest', 
            'USER': 'postgres', 
            'PASSWORD': 'postgres',
            'HOST': 'localhost', 
            'PORT': '5432',
        }

    configure(databases)


def runtests():
    django.setup()
    TestRunner = get_runner(settings)
    test_runner = TestRunner(verbosity=1, interactive=True, failfast=False)
    failures = test_runner.run_tests(['django_seed', ])
    sys.exit(failures)


if __name__ == '__main__':
    runtests()