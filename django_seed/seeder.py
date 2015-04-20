import random
from django_seed.guessers import Name
from django.db.models.fields import *
from django.db.models import ForeignKey, ManyToManyField, OneToOneField, ImageField


class FieldTypeGuesser(object):

    def __init__(self, generator):
        """
        :param generator: Generator
        """
        self.generator = generator

    def guess_format(self, field):

        generator = self.generator
        if isinstance(field, BooleanField): return lambda x: generator.boolean()
        if isinstance(field, NullBooleanField): return lambda x: generator.nullBoolean()
        if isinstance(field, DecimalField): return lambda x: generator.pydecimal(rightDigits=field.decimal_places)
        if isinstance(field, SmallIntegerField): return lambda x: random.randint(0,65535)
        if isinstance(field, IntegerField): return lambda x: random.randint(0,4294967295)
        if isinstance(field, BigIntegerField): return lambda x: random.randint(0,18446744073709551615)
        if isinstance(field, FloatField): return lambda x: generator.pyfloat()
        if isinstance(field, CharField):
            if field.choices:
                return lambda x: generator.randomElement(field.choices)[0]
            return lambda x: generator.text(field.max_length) if field.max_length >= 5 else generator.word()
        if isinstance(field, TextField): return lambda x: generator.text()

        if isinstance(field, DateTimeField): return lambda x: generator.dateTime()
        if isinstance(field, DateField): return lambda x: generator.date()
        if isinstance(field, TimeField): return lambda x: generator.time()

        if isinstance(field, URLField): return lambda x: generator.uri()
        if isinstance(field, SlugField): return lambda x: generator.slug()
        if isinstance(field, IPAddressField):
            protocolIp = generator.randomElements(['ipv4','ipv6'])
            return lambda x: getattr(generator,protocolIp)()
        if isinstance(field, EmailField): return lambda x: generator.email()
        if isinstance(field, ImageField): return lambda x: None

        raise AttributeError(field)


class ModelSeeder(object):
    def __init__(self, model):
        """
        :param model: Generator
        """
        self.model = model
        self.field_formatters = {}

    def guess_field_formatters(self, generator):

        formatters = {}
        model = self.model
        name_guesser = Name(generator)
        fieldTypeGuesser = FieldTypeGuesser(generator)

        for field in model._meta.fields:
        #            yield field.name, getattr(self, field.name)
            field_name = field.name
            if isinstance(field, (ForeignKey,ManyToManyField,OneToOneField)):
                related_model = field.rel.to

                def build_relation(inserted):
                    if related_model in inserted and inserted[related_model]:
                        return related_model.objects.get(pk=random.choice(inserted[related_model]))
                    if not field.null:
                        try :
                            # try to retrieve random object from related_model
                            related_model.objects.order_by('?')[0]
                        except IndexError:
                            raise Exception('Relation "%s.%s" with "%s" cannot be null, check order of add_entity list' % (
                                field.model.__name__, field.name, related_model.__name__,
                            ))
                    return None

                formatters[field_name] = build_relation
                continue

            if isinstance(field, AutoField):
                continue

            formatter = name_guesser.guess_format(field_name)
            if formatter:
                formatters[field_name] = formatter
                continue

            formatter = fieldTypeGuesser.guess_format(field)
            if formatter:
                formatters[field_name] = formatter
                continue

        return formatters

    def execute(self, using, inserted_entities):

        obj = self.model()

        for field, format in self.field_formatters.items():
            if format:
                value = format(inserted_entities) if hasattr(format,'__call__') else format
                setattr(obj, field, value)

        obj.save(using=using)

        return obj.pk


class Seeder(object):

    def __init__(self, generator):
        """
        :param generator: Generator
        """
        self.generator = generator
        self.entities = {}
        self.quantities = {}
        self.orders = []


    def add_entity(self, model, number, customFieldFormatters=None):
        """
        Add an order for the generation of $number records for $entity.

        :param model: mixed A Django Model classname, or a faker.orm.django.EntitySeeder instance
        :type model: Model
        :param number: int The number of entities to seed
        :type number: integer
        :param customFieldFormatters: optional dict with field as key and callable as value
        :type customFieldFormatters: dict or None
        """
        if not isinstance(model, ModelSeeder):
            model = ModelSeeder(model)

        model.field_formatters = model.guess_field_formatters( self.generator )
        if customFieldFormatters:
            model.field_formatters.update(customFieldFormatters)

        klass = model.model
        self.entities[klass] = model
        self.quantities[klass] = number
        self.orders.append(klass)

    def execute(self, using=None):
        """
        Populate the database using all the Entity classes previously added.

        :param using A Django database connection name
        :rtype: A list of the inserted PKs
        """
        if not using:
            using = self.get_connection()

        inserted_entities = {}
        for klass in self.orders:
            number = self.quantities[klass]
            if klass not in inserted_entities:
                inserted_entities[klass] = []
            for i in range(0,number):
                    inserted_entities[klass].append( self.entities[klass].execute(using, inserted_entities) )

        return inserted_entities

    def get_connection(self):
        """
        use the first connection available
        :rtype: Connection
        """

        klass = self.entities.keys()
        if not klass:
            raise AttributeError('No class found from entities. Did you add entities to the Seeder ?')
        klass = list(klass)[0]

        return klass.objects._db
