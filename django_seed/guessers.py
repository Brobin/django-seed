import re


class Name(object):

    def __init__(self, generator):
        self.generator = generator

    def guess_format(self, name):
        name = name.lower()
        generator = self.generator
        if re.findall(r'^is[_A-Z]', name): return lambda x:generator.boolean()
        elif re.findall(r'(_a|A)t$', name): return lambda x:generator.date_time()

        if name in ('first_name', 'firstname', 'first'): return lambda x: generator.first_name()
        if name in ('last_name', 'lastname', 'last'): return lambda x: generator.last_name()

        if name in ('username','login','nickname', 'name'): return lambda x:generator.user_name()
        if name in ('email','email_address'): return lambda x:generator.email()
        if name in ('phone_number','phonenumber','phone'): return lambda x:generator.phone_number()
        if name == 'address' : return lambda x:generator.address()
        if name == 'city' : return lambda x: generator.city()
        if name == 'streetaddress' : return lambda x: generator.street_address()
        if name in ('postcode','zipcode'): return lambda x: generator.postcode()
        if name == 'state' : return lambda x: generator.state()
        if name == 'country' : return lambda x: generator.country()
        if name == 'title' : return lambda x: generator.sentence()
        if name in ('body','summary', 'description'): return lambda x: generator.text()


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
            protocol = generator.randomElements(['ipv4','ipv6'])
            return lambda x: getattr(generator,protocol)()
        if isinstance(field, EmailField): return lambda x: generator.email()
        if isinstance(field, ImageField): return lambda x: None

        raise AttributeError(field)