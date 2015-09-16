from django.apps import apps
from django.core.management.base import BaseCommand

from django_seed import Seed
from django_seed.exceptions import SeederCommandError
from django_seed.toposort import toposort_flatten


class Command(BaseCommand):
    help = 'Seed your Django database with fake data'

    def __init__(self, *args, **kwargs):
        super(Command, self).__init__(*args, **kwargs)

        self.include_models = []
        self.exclude_models = []

        if hasattr(self, 'option_list'):  # Django <=1.7
            self.add_arguments()

    def add_argument(self, parser, *args, **kwargs):
        if parser:  # Django >= 1.8
            parser.add_argument(*args, **kwargs)
        else:  # Django <=1.7
            self.option_list += ( make_option(*args, **kwargs), )

    def add_arguments(self, parser=None):
        if parser:
            self.add_argument(parser, 'applist', metavar='app_label[.ModelName]', nargs='+',
                              help='Restricts seeding to the specified app_label or app_label.ModelName.')
        self.add_argument(parser, '-a', '--all', action='store_true', dest='seed_all', default=False,
                          help="Seed all registered apps.")
        self.add_argument(parser, '-e', '--exclude', dest='exclude', action='append', default=[],
                          help='An app_label or app_label.ModelName to exclude '
                               '(use multiple --exclude to exclude multiple apps/models).')
        self.add_argument(parser, '-n', '--number', type=int, default=10, help="Number of each model to seed.")

    def handle(self, *app_labels, **options):
        number = options.get('number')
        seed_all = options.get('seed_all')
        exclude = options.get('exclude')

        # Exclude models to skip
        self.process_models_from_applist(exclude, self.exclude_model)

        # Add models to seed
        if len(app_labels) == 0:
            if seed_all:  # Add all models from all apps
                for app_config in apps.get_app_configs():
                    for model in app_config.get_models():
                        self.add_model(model)
            else:
                raise SeederCommandError("You must specify a list of apps or the --all flag")
        else:
            self.process_models_from_applist(app_labels, self.add_model)

        seeder = Seed.seeder()

        # don't diplay warnings about non-timezone aware datetimes
        import warnings

        warnings.showwarning = lambda *x: None

        for model in self.prioritized_models():
            seeder.add_entity(model, number)
            print('Seeding %i %ss' % (number, model.__name__))

        pks = seeder.execute()
        print(pks)

    def add_model(self, model):
        if model not in self.include_models:
            self.include_models.append(model)

    def exclude_model(self, model):
        if model not in self.exclude_models:
            self.exclude_models.append(model)

    def process_models_from_applist(self, applist, func):
        for app in applist:
            if '.' in app:  # app.model
                try:
                    model = apps.get_model(app)
                except LookupError:
                    raise SeederCommandError('Unknown model: %s' % app)
                else:
                    func(model)
            else:  # app
                try:
                    app_config = apps.get_app_config(app)
                except LookupError:
                    raise SeederCommandError("Unknown application: %s" % app)
                for model in app_config.get_models():
                    func(model)

    def model_dependencies(self, model):
        dependencies = set()

        if hasattr(model._meta, 'get_fields'):  # Django>=1.8
            for field in model._meta.get_fields():
                if field.many_to_one is True and field.concrete and field.blank is False:
                    dependencies.add(field.related_model)
        else:  # Django<=1.7
            for field in model._meta.fields:
                if isinstance(field, ForeignKey) and field.blank is False:
                    dependencies.add(field.rel.to)
        return dependencies

    def prioritized_models(self):
        dependencies = {}
        models_to_seed = [m for m in self.include_models if m not in self.exclude_models]
        for model in models_to_seed:
            # TODO: dependencies may include models that aren't set to be seeded. How do we handle this?
            dependencies[model] = self.model_dependencies(model)

        try:
            return toposort_flatten(dependencies)
        except ValueError as ex:
            raise SeederCommandError(str(ex))
