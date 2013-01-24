"""

Django-faker uses python-faker to generate test data for Django models and templates.

"""
from django.conf import settings

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
#        assert False, "Cannot create a instance of Faker"
        pass


    @staticmethod
    def getCodename(locale=None, providers=None):
        """
        codename = locale[-Provider]*
        """
        # language
        locale = locale or getattr(settings,'FAKER_LOCALE', getattr(settings,'LANGUAGE_CODE', None))
        # providers
        providers = providers or getattr(settings,'FAKER_PROVIDERS', None)

        codename = locale or 'default'

        if providers:
            codename += "-" + "-".join(sorted(providers))

        return codename


    @classmethod
    def getGenerator(cls, locale=None, providers=None, codename=None):
        """
        use a codename to cache generators
        """

        codename = codename or cls.getCodename(locale, providers)

        if codename not in cls.generators:
            from faker import Faker as FakerGenerator
            # initialize with faker.generator.Generator instance
            # and remember in cache
            cls.generators[codename] = FakerGenerator( locale, providers )
            cls.generators[codename].seed( cls.generators[codename].randomInt() )

        return cls.generators[codename]



    @classmethod
    def getPopulator(cls, locale=None, providers=None):
        """

        uses:

            from django_faker import Faker
            pop = Faker.getPopulator()

            from myapp import models
            pop.addEntity(models.MyModel, 10)
            pop.addEntity(models.MyOtherModel, 10)
            pop.execute()

            pop = Faker.getPopulator('it_IT')

            pop.addEntity(models.MyModel, 10)
            pop.addEntity(models.MyOtherModel, 10)
            pop.execute()

        """

        codename = cls.getCodename(locale, providers)

        if codename not in cls.populators:

            generator = cls.generators.get(codename,  None) or cls.getGenerator(codename=codename)

            from django_faker import populator

            cls.populators[codename] = populator.Populator( generator )

        return cls.populators[codename]

#        if not cls.populator:
#            cls.populator= populators.Populator(
#            # initialize with faker.generator.Generator instance
#            FakerGenerator(
#
#                getattr(settings,'FAKER_LOCALE', getattr(settings,'LANGUAGE_CODE', locale)),
#
#                getattr(settings,'FAKER_PROVIDERS', providers)
#            )
#        )

