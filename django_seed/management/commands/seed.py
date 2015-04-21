
from django.core.management.base import AppCommand
from django_seed import Seed
from django_seed.exceptions import SeederCommandError
from optparse import make_option
import django


class Command(AppCommand):
    help = 'Seed your Django database with fake data'

    args = "[appname ...]"

    option_list = AppCommand.option_list + (
        make_option('--number', dest='number', default=10,
                    help='number of each model to seed'),
    )

    def handle_app_config(self, app_config, **options):
        if app_config.models_module is None:
            raise SeederCommandError('You must provide an app to seed')

        try:
            number = int(options['number'])
        except ValueError:
            raise SeederCommandError('The value of --number must be an integer')

        seeder = Seed.seeder()

        # don't diplay warnings about non-timezone aware datetimes
        import warnings
        warnings.showwarning = lambda *x: None

        for model in app_config.get_models():
            seeder.add_entity(model, number)
            print('Seeding %i %ss' % (number, model.__name__))

        pks = seeder.execute()
        print(pks)

