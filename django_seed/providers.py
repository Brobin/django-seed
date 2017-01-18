
from datetime import timedelta
import random
import time
import uuid
import sys


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

    def duration(self):
        return timedelta(seconds=random.randint(0, int(time.time())))

    def uuid(self):
        return uuid.uuid4()

    def rand_small_int(self, pos=False):
        if pos:
            return random.randint(0, 32767)
        return random.randint(-32768, 32767)

    def rand_int(self, pos=False):
        if pos:
            return random.randint(0, 4294967295)
        return random.randint(-4294967295, 4294967295)

    def rand_big_int(self):
        return random.randint(-sys.maxsize, sys.maxsize)

    def rand_float(self):
        return random.random()

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
