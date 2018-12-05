from django.db.models import *
from django.conf import settings
from django.utils import timezone

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
        if isinstance(field, SlugField): return lambda x: faker.uri_page()
        if isinstance(field, IPAddressField) or isinstance(field, GenericIPAddressField):
            protocol = random.choice(['ipv4','ipv6'])
            return lambda x: getattr(faker, protocol)()
        if isinstance(field, EmailField): return lambda x: faker.email()
        if isinstance(field, CommaSeparatedIntegerField):
            return lambda x: provider.comma_sep_ints()

        if isinstance(field, BinaryField): return lambda x: provider.binary()
        if isinstance(field, ImageField): return lambda x: provider.file_name()
        if isinstance(field, FilePathField): return lambda x: provider.file_name()
        if isinstance(field, FileField): return lambda x: provider.file_name()

        if isinstance(field, CharField):
            if field.choices:
                return lambda x: random.choice(field.choices)[0]
            return lambda x: faker.text(field.max_length) if field.max_length >= 5 else faker.word()
        if isinstance(field, TextField): return lambda x: faker.text()

        if isinstance(field, DateTimeField):
            # format with timezone if it is active
            return lambda x: _timezone_format(faker.date_time())
        if isinstance(field, DateField): return lambda x: faker.date()
        if isinstance(field, TimeField): return lambda x: faker.time()
        raise AttributeError(field)
