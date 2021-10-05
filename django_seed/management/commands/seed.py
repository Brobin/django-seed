import argparse
from django.core.management.base import AppCommand
from django_seed import Seed
from django_seed.exceptions import SeederCommandError
from toposort import toposort_flatten
from collections import defaultdict


class Command(AppCommand):
    help = 'Seed your Django database with fake data.'

    def add_arguments(self, parser: argparse.ArgumentParser):
        super().add_arguments(parser)

        help_text = 'The number of each model to seed (default 10).'
        parser.add_argument('-n', '--number', action='store', nargs='?',
                            default=10, type=int, required=False,
                            help=help_text, dest='number')

        help_text = ('Use this to specify the value a particular field should '
                     'have rather than seeding with Faker.')
        parser.add_argument('--seeder', action='append', nargs=2,
                            required=False, type=str, help=help_text,
                            metavar=('model.field', 'value'), dest='seeder')

    def handle_app_config(self, app_config, **options):
        if app_config.models_module is None:
            raise SeederCommandError('You must provide an app to seed')

        try:
            number = int(options['number'])
        except ValueError:
            raise SeederCommandError('The value of --number must be an integer')

        # Gather seeders
        seeders = defaultdict(dict)

        self.stdout.write(f'Arguments: {options}', style_func=self.style.SUCCESS)

        if options.get('seeder'):
            for model_field, func in options['seeder']:
                model, field = model_field.split('.')
                seeders[model][field] = func
                self.stdout.write(f'Forced model field: {model_field}, seeder value: {func}')

        # Seed
        seeder = Seed.seeder()
        for model in self.sorted_models(app_config):
            if model.__name__ in seeders:
                seeder.add_entity(model, number, seeders[model.__name__])
            else:
                seeder.add_entity(model, number)
            self.stdout.write('Seeding %i %ss' % (number, model.__name__))

        generated = seeder.execute()
        for model, pks in generated.items():
            for pk in pks:
                self.stdout.write(f"Model {model.__name__} generated record with primary key {pk}")

    def get_model_dependencies(self, models):
        dep_dict = {}
        dep_class_map = {}

        for model in models:
            dependencies = set()
            model_replacement = '{}.{}'.format(
                model.__module__,
                model.__name__
            )

            if model_replacement not in dep_class_map:
                dep_class_map[model_replacement] = model

            for field in model._meta.get_fields():
                if ((field.many_to_one is True or field.many_to_many is True or field.one_to_one is True) and
                    field.concrete and field.blank is False):

                    related_model = field.related_model
                    related_model_type = '{}.{}'.format(
                        related_model.__module__,
                        related_model.__name__
                    )
                    replacement = related_model_type

                    if related_model_type not in dep_class_map:
                        dep_class_map[related_model_type] = related_model

                    dependencies.add(replacement)

            dep_dict[model_replacement] = dependencies

        return (dep_dict, dep_class_map)

    def sorted_models(self, app_config):
        dep_dict, dep_class_map = self.get_model_dependencies(app_config.get_models())

        try:
            return [dep_class_map[x] for x in toposort_flatten(dep_dict)]
        except ValueError as ex:
            raise SeederCommandError(str(ex))
