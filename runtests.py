#!/usr/bin/env python
import sys
import django
from django.conf import settings
from django.test.utils import get_runner


def configure():
    from faker import Faker
    fake = Faker()

    settings.configure(
        DATABASES={
            'default': {
                'ENGINE': 'django.db.backends.sqlite3',
                'NAME': ':memory:',
            }
        },
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
    configure()


def runtests():
    django.setup()
    TestRunner = get_runner(settings)
    test_runner = TestRunner(verbosity=1, interactive=True, failfast=False)
    failures = test_runner.run_tests(['django_seed', ])
    sys.exit(failures)


if __name__ == '__main__':
    runtests()