import random
from django_faker.guessers import Name
from django.db.models.fields import *
from django.db.models import ForeignKey, ManyToManyField, OneToOneField, ImageField


class FieldTypeGuesser(object):

    def __init__(self, generator):
        """
        :param generator: Generator
        """
        self.generator = generator

    def guessFormat(self, field):

        generator = self.generator
        if isinstance(field, BooleanField): return lambda x: generator.boolean()
        if isinstance(field, NullBooleanField): return lambda x: generator.nullBoolean()
        if isinstance(field, DecimalField): return lambda x: generator.pydecimal(rightDigits=field.decimal_places)
        if isinstance(field, SmallIntegerField): return lambda x: generator.randomInt(0,65535)
        if isinstance(field, IntegerField): return lambda x: generator.randomInt(0,4294967295)
        if isinstance(field, BigIntegerField): return lambda x: generator.randomInt(0,18446744073709551615)
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


class ModelPopulator(object):
    def __init__(self, model):
        """
        :param model: Generator
        """
        self.model = model
        self.fieldFormatters = {}

    def guessFieldFormatters(self, generator):

        formatters = {}
        model = self.model
        nameGuesser = Name(generator)
        fieldTypeGuesser = FieldTypeGuesser(generator)

        for field in model._meta.fields:
        #            yield field.name, getattr(self, field.name)
            fieldName = field.name
            if isinstance(field, (ForeignKey,ManyToManyField,OneToOneField)):
                relatedModel = field.rel.to

                def build_relation(inserted):
                    if relatedModel in inserted and inserted[relatedModel]:
                        return relatedModel.objects.get(pk=random.choice(inserted[relatedModel]))
                    if not field.null:
                        try :
                            # try to retrieve random object from relatedModel
                            relatedModel.objects.order_by('?')[0]
                        except IndexError:
                            raise Exception('Relation "%s.%s" with "%s" cannot be null, check order of addEntity list' % (
                                field.model.__name__, field.name, relatedModel.__name__,
                            ))
                    return None

                formatters[fieldName] = build_relation
                continue

            if isinstance(field, AutoField):
                continue

            formatter = nameGuesser.guessFormat(fieldName)
            if formatter:
                formatters[fieldName] = formatter
                continue

            formatter = fieldTypeGuesser.guessFormat(field)
            if formatter:
                formatters[fieldName] = formatter
                continue

        return formatters

    def execute(self, using, insertedEntities):

        obj = self.model()

        for field, format in self.fieldFormatters.items():
            if format:
                value = format(insertedEntities) if hasattr(format,'__call__') else format
                setattr(obj, field, value)

        obj.save(using=using)

        return obj.pk


class Populator(object):

    def __init__(self, generator):
        """
        :param generator: Generator
        """
        self.generator = generator
        self.entities = {}
        self.quantities = {}
        self.orders = []


    def addEntity(self, model, number, customFieldFormatters=None):
        """
        Add an order for the generation of $number records for $entity.

        :param model: mixed A Django Model classname, or a faker.orm.django.EntityPopulator instance
        :type model: Model
        :param number: int The number of entities to populate
        :type number: integer
        :param customFieldFormatters: optional dict with field as key and callable as value
        :type customFieldFormatters: dict or None
        """
        if not isinstance(model, ModelPopulator):
            model = ModelPopulator(model)

        model.fieldFormatters = model.guessFieldFormatters( self.generator )
        if customFieldFormatters:
            model.fieldFormatters.update(customFieldFormatters)

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
            using = self.getConnection()

        insertedEntities = {}
        for klass in self.orders:
            number = self.quantities[klass]
            if klass not in insertedEntities:
                insertedEntities[klass] = []
            for i in range(0,number):
                    insertedEntities[klass].append( self.entities[klass].execute(using, insertedEntities) )

        return insertedEntities

    def getConnection(self):
        """
        use the first connection available
        :rtype: Connection
        """

        klass = self.entities.keys()
        if not klass:
            raise AttributeError('No class found from entities. Did you add entities to the Populator ?')
        klass = klass[0]

        return klass.objects._db



