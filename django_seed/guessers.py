
from django.db.models.fields import *
from django.db.models import *
from datetime import timedelta
import time
import django
import random
import re


class NameGuesser(object):

    def __init__(self, faker):
        self.faker = faker

    def guess_format(self, name):
        name = name.lower()
        faker = self.faker
        if re.findall(r'^is[_A-Z]', name): return lambda x:faker.boolean()
        elif re.findall(r'(_a|A)t$', name): return lambda x:faker.date_time()

        if name in ('first_name', 'firstname', 'first'): return lambda x: faker.first_name()
        if name in ('last_name', 'lastname', 'last'): return lambda x: faker.last_name()

        if name in ('username','login','nickname'): return lambda x:faker.user_name()
        if name in ('email','email_address'): return lambda x:faker.email()
        if name in ('phone_number','phonenumber','phone'): return lambda x:faker.phone_number()
        if name == 'address' : return lambda x:faker.address()
        if name == 'city' : return lambda x: faker.city()
        if name == 'streetaddress' : return lambda x: faker.street_address()
        if name in ('postcode','zipcode'): return lambda x: faker.postcode()
        if name == 'state' : return lambda x: faker.state()
        if name == 'country' : return lambda x: faker.country()
        if name == 'title' : return lambda x: faker.sentence()
        if name in ('body','summary', 'description'): return lambda x: faker.text()


class FieldTypeGuesser(object):

    def __init__(self, faker):
        """
        :param faker: Generator
        """
        self.faker = faker

    def guess_format(self, field):
        faker = self.faker
        if isinstance(field, BooleanField): return lambda x: faker.boolean()
        if isinstance(field, NullBooleanField): return lambda x: faker.null_boolean()
        if isinstance(field, DecimalField): return lambda x: random.random()
        if isinstance(field, PositiveSmallIntegerField): return lambda x: random.randint(0, 65535)
        if isinstance(field, SmallIntegerField): return lambda x: random.randint(-65535, 65535)
        if isinstance(field, PositiveIntegerField): return lambda x: random.randint(0, 4294967295)
        if isinstance(field, IntegerField): return lambda x: random.randint(-4294967295, 4294967295)
        if isinstance(field, BigIntegerField): return lambda x: random.randint(0, 18446744073709551615)
        if isinstance(field, FloatField): return lambda x: random.random()

        if isinstance(field, URLField): return lambda x: faker.uri()
        if isinstance(field, SlugField): return lambda x: faker.uri_page()
        if isinstance(field, IPAddressField) or isinstance(field, GenericIPAddressField):
            protocol = random.choice(['ipv4','ipv6'])
            return lambda x: getattr(faker, protocol)()
        if isinstance(field, EmailField): return lambda x: faker.email()
        if isinstance(field, ImageField): return lambda x: None

        if isinstance(field, CharField):
            if field.choices:
                return lambda x: random.choice(field.choices)[0]
            return lambda x: faker.text(field.max_length) if field.max_length >= 5 else faker.word()
        if isinstance(field, TextField): return lambda x: faker.text()

        if django.VERSION[1] >= 8 and isinstance(field, DurationField):
            return lambda x: timedelta(seconds=random.randint(0, int(time.time())))
        if isinstance(field, DateTimeField): return lambda x: faker.date_time()
        if isinstance(field, DateField): return lambda x: faker.date()
        if isinstance(field, TimeField): return lambda x: faker.time()
        raise AttributeError(field)