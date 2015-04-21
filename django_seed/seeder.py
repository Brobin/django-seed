import random
from django_seed.guessers import NameGuesser, FieldTypeGuesser
from django_seed.exceptions import SeederException
from django.db.models.fields import AutoField
from django.db.models import ForeignKey, ManyToManyField, OneToOneField


class ModelSeeder(object):

    def __init__(self, model):
        """
        :param model: Generator
        """
        self.model = model
        self.field_formatters = {}

    def guess_field_formatters(self, faker):

        formatters = {}
        model = self.model
        name_guesser = NameGuesser(faker)
        field_type_guesser = FieldTypeGuesser(faker)

        for field in model._meta.fields:
            field_name = field.name
            if isinstance(field, (ForeignKey, ManyToManyField, OneToOneField)):
                related_model = field.rel.to

                def build_relation(inserted):
                    if related_model in inserted and inserted[related_model]:
                        pk = random.choice(inserted[related_model])
                        return related_model.objects.get(pk=pk)
                    if not field.null:
                        try :
                            # try to retrieve random object from related_model
                            related_model.objects.order_by('?')[0]
                        except IndexError:
                            message = 'Field {} cannot be null'.format(field)
                            raise SeederException(message)
                    return None

                formatters[field_name] = build_relation
                continue

            if isinstance(field, AutoField):
                continue

            if not field.choices:
                formatter = name_guesser.guess_format(field_name)
                if formatter:
                    formatters[field_name] = formatter
                    continue

            formatter = field_type_guesser.guess_format(field)
            if formatter:
                formatters[field_name] = formatter
                continue

        return formatters

    def execute(self, using, inserted_entities):

        obj = self.model()

        for field, format in self.field_formatters.items():
            if format:
                if hasattr(format,'__call__'):
                    setattr(obj, field, format(inserted_entities))
                else:
                    setattr(obj, field, format)

        obj.save(using=using)

        return obj.pk


class Seeder(object):

    def __init__(self, faker):
        """
        :param faker: Generator
        """
        self.faker = faker
        self.entities = {}
        self.quantities = {}
        self.orders = []


    def add_entity(self, model, number, customFieldFormatters=None):
        """
        Add an order for the generation of $number records for $entity.

        :param model: mixed A Django Model classname,
        or a faker.orm.django.EntitySeeder instance
        :type model: Model
        :param number: int The number of entities to seed
        :type number: integer
        :param customFieldFormatters: optional dict with field as key and 
        callable as value
        :type customFieldFormatters: dict or None
        """
        if not isinstance(model, ModelSeeder):
            model = ModelSeeder(model)

        model.field_formatters = model.guess_field_formatters(self.faker)
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
                entity = self.entities[klass].execute(using, inserted_entities)
                inserted_entities[klass].append(entity)

        return inserted_entities

    def get_connection(self):
        """
        use the first connection available
        :rtype: Connection
        """

        klass = self.entities.keys()
        if not klass:
            message = 'No classed found. Did you add entities to the Seeder?'
            raise SeederException(message)
        klass = list(klass)[0]

        return klass.objects._db
