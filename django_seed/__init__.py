
from django.conf import settings
import random


__version__ = '0.2'


class Faker(object):
    instance = None
    populators = {}
    generators = {}

    @classmethod
    def __new__(cls, *args, **kwargs):
        if cls.instance is None:
            cls.instance = super(Faker, cls).__new__(*args, **kwargs)
        return cls.instance

    def __init__(self):
        pass

    @staticmethod
    def codename(locale=None):
        locale = locale or getattr(settings,'LANGUAGE_CODE', None)
        codename = locale or 'default'
        return codename

    @classmethod
    def generator(cls, locale=None, codename=None):
        codename = codename or cls.codename(locale)
        if codename not in cls.generators:
            from faker import Faker as FakerGenerator
            # initialize with faker.generator.Generator instance
            # and remember in cache
            cls.generators[codename] = FakerGenerator(locale)
            cls.generators[codename].seed(random.randint(1,10000))
        return cls.generators[codename]

    @classmethod
    def populator(cls, locale=None):
        codename = cls.codename(locale)
        if codename not in cls.populators:
            generator = cls.generators.get(codename,  None) or cls.getGenerator(codename=codename)
            from django_faker import populator
            cls.populators[codename] = populator.Populator(generator)

        return cls.populators[codename]

