
from django.core.management.base import AppCommand, CommandError
from optparse import make_option
import django


class Command(AppCommand):
    help = 'Generates DRF API Views and Serializers for a Django app'

    args = "[appname ...]"

    option_list = AppCommand.option_list + (
        make_option('-n', '--number', dest='number', default=10,
                    help='number of each model to seed'),
    )

    def handle_app_config(self, app_config, **options):
        if app_config.models_module is None:
            raise CommandError('You must provide an app to generate an API')

        print('Seeding models')
