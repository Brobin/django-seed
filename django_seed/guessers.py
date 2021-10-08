from django.db.models import *
try:
    # JSONField is not defined in Django versions < 2 or might be in
    # another import path for versions >= 2.
    from django.db.models import JSONField
except ImportError:
    from django.contrib.postgres.fields import JSONField
from django.conf import settings
from django.core.validators import validate_comma_separated_integer_list
from django.utils import timezone
from django.contrib.postgres.fields import ArrayField

import random
import re

from .providers import Provider


def _timezone_format(value):
    """
    Generates a timezone aware datetime if the 'USE_TZ' setting is enabled

    :param value: The datetime value
    :return: A locale aware datetime
    """
    if getattr(settings, 'USE_TZ', False):
        return timezone.make_aware(value, timezone.get_current_timezone(), is_dst=False)
    return value


class NameGuesser(object):

    def __init__(self, faker):
        self.faker = faker

    def guess_format(self, name):
        """
        Returns a faker method based on the field's name
        :param name:
        """
        name = name.lower()
        faker = self.faker
        if re.findall(r'^is[_A-Z]', name): return lambda x: faker.boolean()
        elif re.findall(r'(_a|A)t$', name): return lambda x: _timezone_format(faker.date_time())

        if name in ('first_name', 'firstname', 'first'): return lambda x: faker.first_name()
        if name in ('last_name', 'lastname', 'last'): return lambda x: faker.last_name()

        if name in ('username', 'login', 'nickname'): return lambda x:faker.user_name()
        if name in ('email', 'email_address'): return lambda x:faker.email()
        if name in ('phone_number', 'phonenumber', 'phone'): return lambda x:faker.phone_number()
        if name == 'address': return lambda x:faker.address()
        if name == 'city': return lambda x: faker.city()
        if name == 'streetaddress': return lambda x: faker.street_address()
        if name in ('postcode', 'zipcode'): return lambda x: faker.postcode()
        if name == 'state': return lambda x: faker.state()
        if name == 'country': return lambda x: faker.country()
        if name == 'title': return lambda x: faker.sentence()
        if name in ('body', 'summary', 'description'): return lambda x: faker.text()


class FieldTypeGuesser(object):

    def __init__(self, faker):
        """
        :param faker: Generator
        """
        self.faker = faker
        self.provider = Provider(self.faker)

    def guess_format(self, field):
        """
        Returns the correct faker function based on the field type
        :param field:
        """
        faker = self.faker
        provider = self.provider

        if field.choices:
            collected_choices = []
            for choice in field.choices:
                # Check if we have choices that are in named groups
                # https://docs.djangoproject.com/en/3.2/ref/models/fields/#choices
                if type(choice[1]) != str:
                    for named_choice in choice[1]:
                        collected_choices.append(named_choice)
                else:
                    collected_choices.append(choice)

            return lambda x: random.choice(collected_choices)[0]

        if isinstance(field, DurationField): return lambda x: provider.duration()
        if isinstance(field, UUIDField): return lambda x: provider.uuid()

        if isinstance(field, BooleanField): return lambda x: faker.boolean()
        if isinstance(field, NullBooleanField): return lambda x: faker.null_boolean()
        if isinstance(field, PositiveSmallIntegerField): return lambda x: provider.rand_small_int(pos=True)
        if isinstance(field, SmallIntegerField): return lambda x: provider.rand_small_int()
        if isinstance(field, BigIntegerField): return lambda x: provider.rand_big_int()
        if isinstance(field, PositiveIntegerField): return lambda x: provider.rand_small_int(pos=True)
        if isinstance(field, IntegerField): return lambda x: provider.rand_small_int()
        if isinstance(field, FloatField): return lambda x: provider.rand_float()
        if isinstance(field, DecimalField): return lambda x: random.random()

        if isinstance(field, URLField): return lambda x: faker.uri()
        if isinstance(field, SlugField): return lambda x: faker.slug()
        if isinstance(field, IPAddressField) or isinstance(field, GenericIPAddressField):
            protocol = random.choice(['ipv4', 'ipv6'])
            return lambda x: getattr(faker, protocol)()
        if isinstance(field, EmailField): return lambda x: faker.email()
        if isinstance(field, CommaSeparatedIntegerField) or \
                (isinstance(field, CharField) and (validate_comma_separated_integer_list in field.validators)):
            return lambda x: provider.comma_sep_ints()

        if isinstance(field, BinaryField): return lambda x: provider.binary()
        if isinstance(field, ImageField): return lambda x: provider.file_name()
        if isinstance(field, FilePathField): return lambda x: provider.file_name()
        if isinstance(field, FileField): return lambda x: provider.file_name()

        if isinstance(field, CharField):
            return lambda x: faker.text(field.max_length) if field.max_length >= 5 else faker.word()
        if isinstance(field, TextField): return lambda x: faker.text()

        if isinstance(field, DateTimeField):
            # format with timezone if it is active
            return lambda x: _timezone_format(faker.date_time())
        if isinstance(field, DateField): return lambda x: faker.date()
        if isinstance(field, TimeField): return lambda x: faker.time()
        if isinstance(field, ArrayField):
            return lambda x: [self.guess_format(field.base_field)(1)]

        if isinstance(field, JSONField):
            def json_generator(_, data_columns: list = None, num_rows: int = 10, indent: int = None) -> str:
                return faker.json(data_columns=data_columns, num_rows=num_rows, indent=indent)
            return json_generator

        # TODO: This should be fine, but I can't find any models that I can use
        # in a simple test case.
        if hasattr(field, '_default_hint'): return lambda x: field._default_hint[1]
        raise AttributeError(field)
