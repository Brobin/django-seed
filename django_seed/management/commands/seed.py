
from django.core.management.base import AppCommand
from django_seed import Seed
from django_seed.exceptions import SeederCommandError
from django_seed.toposort import toposort_flatten
from optparse import make_option


class Command(AppCommand):
    help = 'Seed your Django database with fake data'

    args = "[appname ...]"

    option_list = [
        make_option('--number', dest='number', default=10,
                    help='number of each model to seed (default 10)'),
    ]

    def add_arguments(self, parser):
        super(Command, self).add_arguments(parser)

        help_text = 'number of each model to seed (default 10)'
        parser.add_argument('--number', nargs='?', type=int, default=10, const=10, help=help_text)

    def handle_app_config(self, app_config, **options):
        if app_config.models_module is None:
            raise SeederCommandError('You must provide an app to seed')

        try:
            number = int(options['number'])
        except ValueError:
            raise SeederCommandError('The value of --number must be an integer')

        seeder = Seed.seeder()

        for model in self.sorted_models(app_config):
            seeder.add_entity(model, number)
            print('Seeding %i %ss' % (number, model.__name__))

        generated = seeder.execute()

        for model, pks in generated.items():
            for pk in pks:
                print("Model {} generated record with primary key {}".format(
                    model.__name__,
                    pk
                ))

    def dependencies(self, model):
        dependencies = set()

        for field in model._meta.get_fields():
            if field.many_to_one is True and field.concrete and field.blank is False:
                dependencies.add(field.related_model)

        return dependencies

    def sorted_models(self, app_config):
        dependencies = {}
        for model in app_config.get_models():
            dependencies[model] = self.dependencies(model)
        try:
            return toposort_flatten(dependencies)
        except ValueError as ex:
            raise SeederCommandError(str(ex))
