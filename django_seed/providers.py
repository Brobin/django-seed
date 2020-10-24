
from datetime import timedelta
import random
import time
import uuid
import sys
from django.forms import Field


file_extensions = ("flac", "mp3", "wav", "bmp", "gif", "jpeg", "jpg", "png",
                   "tiff", "css", "csv", "html", "js", "json", "txt", "mp4",
                   "avi", "mov", "webm")


class Provider(object):
    """
    Provider class contains methods for random data that are not
    provided in the faker package... yet :D
    """

    def __init__(self, faker):
        self.faker = faker
        self.rand_small_ints = {}
        self.rand_ints = {}
        self.rand_big_ints = {}
        self.rand_floats = {}
        self.unique_field_texts = {}



    def duration(self):
        return timedelta(seconds=random.randint(0, int(time.time())))

    def uuid(self):
        return uuid.uuid4()

    def rand_small_int(self, pos=False, field=None):
        start = 0 if pos else -32768
        randnum = random.randint(start, 32767)

        if field and field.unique:
            if not self.rand_small_ints.get(field):
                self.rand_small_ints[field] = []

            while randnum in self.rand_small_ints[field]:
                randnum = random.randint(start, 32767)

            self.rand_small_ints[field].append(randnum)

        return randnum

    def rand_int(self, pos=False, field=None):
        start = 0 if pos else -4294967295
        randnum = random.randint(start, 4294967295)

        if field and field.unique:
            if not self.rand_ints.get(field):
                self.rand_ints[field] = []

            while randnum in self.rand_ints[field]:
                randnum = random.randint(start, 4294967295)

            self.rand_ints[field].append(randnum)

        return randnum

    def rand_big_int(self, field=None):
        randnum = random.randint(-sys.maxsize, sys.maxsize)

        if field and field.unique:
            if not self.rand_big_ints.get(field):
                self.rand_big_ints[field] = []

            while randnum in self.rand_big_ints[field]:
                randnum = random.randint(-sys.maxsize, sys.maxsize)

            self.rand_big_ints[field].append(randnum)

        return randnum

    def rand_float(self, field=None):
        randnum = random.random()

        if field and field.unique:
            if not self.rand_floats.get(field):
                self.rand_floats[field] = []

            while randnum in self.rand_floats[field]:
                randnum = random.random()

            self.rand_floats[field].append(randnum)

        return randnum

    def file_name(self):
        filename = self.faker.word()
        extension = random.choice(file_extensions)
        return '{0}.{1}'.format(filename, extension)

    def comma_sep_ints(self):
        ints = [str(self.rand_int()) for x in range(10)]
        return ','.join(ints)

    def binary(self):
        word = self.faker.text(512)
        return str.encode(str(word))

    def get_unique_string(self, field):
        if not self.unique_field_texts.get(field):
            self.unique_field_texts[field] = []

        if field.default:
            self.unique_field_texts[field].append(field.default)

        text = self.faker.text(field.max_length) if field.max_length >= 5 else self.faker.word()
        text = text[:field.max_length]
        while text in self.unique_field_texts[field]:
            text = self.faker.text(field.max_length) if field.max_length >= 5 else self.faker.word()
            text = text[:field.max_length]

        self.unique_field_texts[field].append(text)
        return text

    def rand_text(self, faker, field=None):
        if field.unique:
            return self.get_unique_string(field)

        elif field.choices:
            return random.choice(field.choices)[0]

        return faker.text(field.max_length)[:field.max_length] if \
            field.max_length >= 5 else faker.word()[:field.max_length]
