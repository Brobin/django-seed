from django.apps import apps
from django.core.management.base import BaseCommand
from django_seed import Seed
from django_seed.exceptions import SeederCommandError


class Command(BaseCommand):
    help = 'Seed your Django database with fake data'

    def add_arguments(self, parser):
        parser.add_argument('args', metavar='app_label[.ModelName]', nargs='*',
                            help='Restricts seeding to the specified app_label or app_label.ModelName.')
        parser.add_argument('-a', '--all', action='store_true', dest='seed_all', default=False,
                            help="Seed all registered apps.")
        parser.add_argument('-n', '--number', type=int, default=10, help="Number of each model to seed.")

    def add_model(self, model):
        if model not in self.models:
            self.models.append(model)

    def handle(self, *app_labels, **options):
        number = options.get('number')
        seed_all = options.get('seed_all')

        # Collect all models
        self.models = []

        if len(app_labels) == 0:
            if seed_all:  # Add all models from all apps
                for app_config in apps.get_app_configs():
                    for model in app_config.get_models():
                        self.add_model(model)
            else:
                raise SeederCommandError("You must specify a list of apps or the --all flag")
        else:
            for label in app_labels:
                try:
                    app_label, model_label = label.split('.')
                except ValueError:
                    # This is just an app - no model qualifier
                    app_label = label
                    try:
                        app_config = apps.get_app_config(app_label)
                    except LookupError:
                        raise SeederCommandError("Unknown application: %s" % app_label)
                    for model in app_config.get_models():
                        self.add_model(model)
                else:
                    # app.model specified
                    try:
                        app_config = apps.get_app_config(app_label)
                    except LookupError:
                        raise SeederCommandError("Unknown application: %s" % app_label)
                    try:
                        model = app_config.get_model(model_label)
                    except LookupError:
                        raise SeederCommandError("Unknown model: %s.%s" % (app_label, model_label))
                    self.add_model(model)

        seeder = Seed.seeder()

        # don't diplay warnings about non-timezone aware datetimes
        import warnings

        warnings.showwarning = lambda *x: None

        for model in self.models:
            seeder.add_entity(model, number)
            print('Seeding %i %ss' % (number, model.__name__))

        pks = seeder.execute()
        print(pks)