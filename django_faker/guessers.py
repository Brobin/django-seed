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