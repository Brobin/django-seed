from django.core.management.base import CommandError


class SeederException(Exception):
    pass


class SeederCommandError(CommandError):
    pass
