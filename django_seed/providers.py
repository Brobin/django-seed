
from datetime import timedelta
import random
import time
import uuid
import sys


class Provider(object):
    """
    Provider class contains methods for random data that are not
    provided in the faker package.
    """

    def duration(cls):
        return timedelta(seconds=random.randint(0, int(time.time())))

    def uuid(cls):
        return uuid.uuid4()

    def rand_small_int(cls, pos=False):
        if pos:
            return random.randint(0, 65535)
        return random.randint(-65535, 65535)

    def rand_int(cls, pos=False):
        if pos:
            return random.randint(0, 4294967295)
        return random.randint(-4294967295, 4294967295)

    def rand_big_int(cls):
        return random.randint(-sys.maxsize, sys.maxsize)

    def rand_float(cls):
        return random.random()
