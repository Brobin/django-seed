
from django.conf import settings
import random


__version__ = '0.2'


class Seed(object):
    instance = None
    seeders = {}
    fakers = {}

    @classmethod
    def __new__(cls, *args, **kwargs):
        if cls.instance is None:
            cls.instance = super(Seed, cls).__new__(*args, **kwargs)
        return cls.instance

    def __init__(self):
        pass

    @staticmethod
    def codename(locale=None):
        locale = locale or getattr(settings,'LANGUAGE_CODE', None)
        codename = locale or 'default'
        return codename

    @classmethod
    def faker(cls, locale=None, codename=None):
        codename = codename or cls.codename(locale)
        if codename not in cls.fakers:
            from faker import Faker as Faker
            # initialize with faker.faker.Generator instance
            # and remember in cache
            cls.fakers[codename] = Faker(locale)
            cls.fakers[codename].seed(random.randint(1,10000))
        return cls.fakers[codename]

    @classmethod
    def seeder(cls, locale=None):
        codename = cls.codename(locale)
        if codename not in cls.seeders:
            faker = cls.fakers.get(codename,  None) or cls.faker(codename=codename)
            from django_seed import seeder
            cls.seeders[codename] = seeder.Seeder(faker)

        return cls.seeders[codename]

