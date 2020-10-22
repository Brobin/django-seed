import random

from contextlib import contextmanager
from datetime import datetime

from django import VERSION as django_version
from django.conf import settings
from django.core.management import call_command
from django.core.validators import validate_comma_separated_integer_list
from django.db import models
from django.utils import timezone
from django.contrib.postgres.fields import ArrayField

from django_seed.guessers import NameGuesser, FieldTypeGuesser
from django_seed.seeder import Seeder
from django_seed.exceptions import SeederException, SeederCommandError
from django_seed import Seed

from faker import Faker
from alphabet_detector import AlphabetDetector
from jsonfield import JSONField

try:
    from django.utils.unittest import TestCase
except:
    from django.test import TestCase
from unittest import skipIf

fake = Faker()

DEF_LD = "default long description"
DEF_SD = "default short description"

@contextmanager
def django_setting(name, value):
    """
    Generator that mutates the django.settings object during the context of a test run.

    :param name: The setting name to be affected
    :param value: The setting value to be defined during the execution
    :return:
    """
    original_value = getattr(settings, name)
    setattr(settings, name, value)

    try:
        yield
    finally:
        setattr(settings, name, original_value)

# Game models
class Game(models.Model):
    title = models.CharField(max_length=200)
    slug = models.SlugField(max_length=200)
    description = models.TextField()
    game_started = models.DateTimeField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    updated_date = models.DateField()
    updated_time = models.TimeField()
    active = models.BooleanField()
    max_score = models.BigIntegerField()
    levels = models.SmallIntegerField()
    likes = models.IntegerField()
    random_binary = models.BinaryField()


class Player(models.Model):
    nickname = models.CharField(max_length=100)
    tagline = models.CharField(max_length=128)
    avatar = models.FilePathField()
    score = models.BigIntegerField()
    last_login_at = models.DateTimeField()
    game = models.ForeignKey(to=Game, on_delete=models.CASCADE)
    ip = models.GenericIPAddressField()
    achievements = models.CharField(validators=[validate_comma_separated_integer_list], max_length=1000)
    friends = models.PositiveIntegerField()
    balance = models.FloatField()

class Action(models.Model):
    ACTION_FIRE = 'fire'
    ACTION_MOVE = 'move'
    ACTION_STOP = 'stop'
    ACTIONS = (
        (ACTION_FIRE, 'Fire'),
        (ACTION_MOVE, 'Move'),
        (ACTION_STOP, 'Stop'),
    )
    name = models.CharField(max_length=4, choices=ACTIONS)
    executed_at = models.DateTimeField()
    duration = models.DurationField()
    uuid = models.UUIDField()
    actor = models.ForeignKey(to=Player,on_delete=models.CASCADE,related_name='actions', null=False)
    target = models.ForeignKey(to=Player,on_delete=models.CASCADE, related_name='enemy_actions+', null=True)

# Product models
class Product(models.Model):
    name = models.CharField(max_length=100)
    short_description = models.CharField(max_length=100, default=DEF_SD)
    description = models.TextField(default=DEF_LD)
    enabled = models.BooleanField(default=True)

class Customer(models.Model):
    name = models.CharField(max_length=255)
    country = models.CharField(max_length=30)
    address = models.CharField(max_length=50)
    created_at = models.DateTimeField(auto_now=False, auto_now_add=True)
    comments = models.TextField(max_length=500)

# Reporter models
class Pen(models.Model):
    ink_left = models.PositiveIntegerField()


class Reporter(models.Model):
    name = models.CharField(max_length=100)
    pen = models.OneToOneField(
        Pen,
        on_delete=models.CASCADE,
    )


class Article(models.Model):
    title = models.CharField(max_length=100)
    reporter = models.ForeignKey(Reporter, on_delete=models.CASCADE)


class Newspaper(models.Model):
    name = models.CharField(max_length=100)
    address = models.CharField(max_length=80)
    articles = models.ForeignKey(Article, on_delete=models.CASCADE)

    # A reporter works for multiple newspapers
    reporters = models.ManyToManyField(Reporter)


class NotCoveredFields(models.Model):
    json = JSONField()


# This model should only be created when Postgres is being used
class PhoneNumberPerson(models.Model):
    phones = ArrayField(
        base_field=models.CharField(
            ("Phone Number"),
            max_length=50,
            unique=True
        )
    ) if 'postgres' in settings.DATABASES else None


class NameGuesserTestCase(TestCase):

    def setUp(self):
        self.instance = NameGuesser(fake)

    def test_guess_format_timezone(self):
        test_names = ('something_at', 'something_At', 'gameUpdated_At', 'game_created_at')

        with django_setting('USE_TZ', True):
            for name in test_names:
                value = self.instance.guess_format(name)(datetime.now())
                self.assertTrue(timezone.is_aware(value))

        with django_setting('USE_TZ', False):
            for name in test_names:
                value = self.instance.guess_format(name)(datetime.now())
                self.assertFalse(timezone.is_aware(value))


class FieldTypeGuesserTestCase(TestCase):

    def setUp(self):
        self.instance = FieldTypeGuesser(fake)

    def test_guess_with_datetime(self):
        generator = self.instance.guess_format(models.DateTimeField())

        with django_setting('USE_TZ', True):
            value = generator(datetime.now())
            self.assertTrue(timezone.is_aware(value))

        with django_setting('USE_TZ', False):
            value = generator(datetime.now())
            self.assertFalse(timezone.is_aware(value))

    @skipIf(django_version[0] < 2, "JSONField does not work with Django 1.11")
    def test_guess_not_in_format(self):
        from django.contrib.postgres.fields.jsonb import JSONField
        # postgres native JSONField has the _default_hint
        generator = self.instance.guess_format(JSONField())
        self.assertEquals(generator({}), '{}')

class SeederTestCase(TestCase):

    def test_population(self):
        faker = fake
        seeder = Seeder(faker)
        seeder.add_entity(Game, 10)
        self.assertEqual(len(seeder.execute()[Game]), 10)
        self.assertEqual(len(Game.objects.all()), 10)

        seeder.add_entity(Game, 40)
        self.assertEqual(len(seeder.execute()[Game]), 40)
        self.assertEqual(len(Game.objects.all()), 50)

    def test_same_model_unique_fields(self):
        faker = fake
        seeder = Seeder(faker)
        seeder.add_entity(Game, 10, {
            "title": "First Game"
        })

        seeder.add_entity(Game, 20, {
            "title": "Second Game"
        })

        inserted_pks = seeder.execute()

        self.assertEqual(len(inserted_pks[Game]), 30)
        self.assertEqual(len(Game.objects.all()), 30)
        self.assertEqual(Game.objects.get(id=inserted_pks[Game][0]).title, "First Game")
        self.assertEqual(Game.objects.get(id=inserted_pks[Game][-1]).title, "Second Game")

    def test_guesser(self):
        faker = fake
        def title_fake(arg):
            title_fake.count += 1
            name = faker.company()
            return name
        title_fake.count = 0
        seeder = Seeder(faker)
        seeder.add_entity(Game, 10, {
            'title': title_fake
        })
        self.assertEqual(len(seeder.execute()[Game]), title_fake.count)

    def valid_player(self, player):
        p = player
        return 0 <= p.score <= 1000 and '@' in p.nickname

    def test_formatter(self):
        faker = fake
        seeder = Seeder(faker)
        seeder.add_entity(Game, 5)
        seeder.add_entity(Player, 10, {
            'score': lambda x: random.randint(0, 1000),
            'nickname': lambda x: fake.email()
        })
        seeder.add_entity(Action, 30)
        inserted_pks = seeder.execute()
        self.assertTrue(len(inserted_pks[Game]) == 5)
        self.assertTrue(len(inserted_pks[Player]) == 10)

        players = Player.objects.all()
        self.assertTrue(any([self.valid_player(p) for p in players]))

    @skipIf(django_version[0] < 2, "JSONField does not work with Django 1.11")
    def test_not_covered_fields(self):
        """
        Tell the django-seed how to work with fields which are
        not covered by the code. Avoids AttributeError(field).
        :return:
        """
        faker = fake
        seeder = Seeder(faker)
        seeder.add_entity(NotCoveredFields, 10, {
            'json': lambda x: {seeder.faker.domain_name(): {'description': seeder.faker.text()}},
        })
        inserted_pks = seeder.execute()
        self.assertTrue(len(inserted_pks[NotCoveredFields]) == 10)
        self.assertTrue(all([field.json for field in NotCoveredFields.objects.all()]))

    def test_locale(self):
        ad = AlphabetDetector()
        faker = Faker('ru_RU')
        seeder = Seeder(faker)
        seeder.add_entity(Game, 5)
        seeder.execute()
        self.assertTrue(all([ad.is_cyrillic(game.title) for game in Game.objects.all()]))

    def test_null_foreign_key(self):
        faker = fake
        seeder = Seeder(faker)
        try:
            seeder.add_entity(Action, 1)
            seeder.execute()
        except Exception as e:
            self.assertTrue(isinstance(e, SeederException))
        pass

    def test_no_entities_added(self):
        faker = fake
        seeder = Seeder(faker)
        try:
            seeder.execute()
        except Exception as e:
            self.assertTrue(isinstance(e, SeederException))

    def test_auto_now_add(self):
        date = datetime(1957, 3, 6, 13, 13)
        faker = fake
        seeder = Seeder(faker)
        seeder.add_entity(Game, 10, {
            'created_at': lambda x: date
        })
        inserted_pks = seeder.execute()[Game]

        games = Game.objects.filter(pk__in=inserted_pks)
        self.assertTrue(all(game.created_at == date for game in games))

    def test_auto_now(self):
        date = datetime(1957, 3, 6, 13, 13)
        faker = fake
        seeder = Seeder(faker)
        seeder.add_entity(Game, 10, {
            'updated_at': lambda x: date
        })
        inserted_pks = seeder.execute()[Game]

        games = Game.objects.filter(pk__in=inserted_pks)
        self.assertTrue(all(game.updated_at == date for game in games))


class APISeedTestCase(TestCase):

    def setUp(self):
        self.seed1 = Seed()
        self.seed2 = Seed()

    def test_django_seed_singleton(self):
        self.assertEqual(self.seed1, self.seed2)
        self.assertIs(self.seed1, self.seed1)

    def test_faker_cache_faker(self):
        gen1 = self.seed1.faker()
        gen2 = self.seed2.faker()
        self.assertIs(gen1, gen2)

        gen1 = self.seed1.faker(codename='default')
        gen2 = self.seed2.faker(codename='default')
        self.assertIs(gen1, gen2)

        gen1 = self.seed1.faker(locale='it_IT')
        gen2 = self.seed2.faker(locale='it_IT')
        self.assertIs(gen1, gen2)

    def test_faker_cache_seeder(self):
        seeder1 = self.seed1.seeder()
        seeder2 = self.seed2.seeder()
        self.assertIs(seeder1, seeder2)

        gen1 = seeder1.faker
        gen2 = seeder2.faker
        self.assertIs(gen1, gen2)

        seeder1 = self.seed1.seeder(locale='it_IT')
        seeder2 = self.seed2.seeder(locale='it_IT')
        self.assertIs(seeder1, seeder2)


class SeedCommandTestCase(TestCase):

    def test_seed_command(self):
        call_command('seed', 'django_seed', number=10)

    def test_invalid_number_arg(self):
        try:
            call_command('seed', 'django_seed', number='asdf')
        except Exception as e:
            self.assertTrue(isinstance(e, SeederCommandError))
        pass

    def test_seed_command_forced_field(self):
        call_command('seed', 'django_seed', '--seeder', 'Customer.name', 'BobbyLongName', '--number=12')

        customers = Customer.objects.all()
        
        self.assertTrue(customers[0].name == 'BobbyLongName')
        self.assertTrue(len(customers) == 12)

class DefaultValueTestCase(TestCase):

    def test_default_value_guessed_by_field_type(self):
        faker = fake
        seeder = Seeder(faker)

        seeder.add_entity(Product, 1, {'name':'Awesome Product'})
        _id = seeder.execute()

        self.assertIsNotNone(_id)

        product = Product.objects.get(id=_id[Product][0])

        self.assertEquals(product.short_description, DEF_SD)
        self.assertTrue(product.enabled)

    def test_default_value_guessed_by_field_name(self):
        faker = fake
        seeder = Seeder(faker)

        seeder.add_entity(Product, 1, {'name':'Great Product'})
        _id = seeder.execute()

        self.assertIsNotNone(_id)

        product = Product.objects.get(id=_id[Product][0])

        self.assertEquals(product.description, DEF_LD)

class LengthRulesTestCase(TestCase):

    def test_max_length(self):
        faker = fake
        seeder = Seeder(faker)

        name_max_len = Customer._meta.get_field('name').max_length
        country_max_len = Customer._meta.get_field('country').max_length
        address_max_len = Customer._meta.get_field('address').max_length
        comments_max_len = Customer._meta.get_field('comments').max_length

        rand = random.randint(1, 10)

        data = {
            'name': 'x' * (name_max_len + rand),
            'country': 'p' * (country_max_len + rand),
            'address': 't' * (address_max_len + rand),
            'comments': 'o' * (comments_max_len + rand),
        }

        seeder.add_entity(Customer, 1, data)
        _id = seeder.execute()

        customer = Customer.objects.get(id=_id[Customer][0])

        self.assertTrue(len(customer.name) <= name_max_len,
            "name with length {}, does not respect max length restriction of {}"
            .format(len(customer.name), name_max_len))

        self.assertTrue(len(customer.country) <= country_max_len,
            "country with length {}, does not respect max length restriction of {}"
            .format(len(customer.name), country_max_len))

        self.assertTrue(len(customer.address) <= address_max_len,
            "address with length {}, does not respect max length restriction of {}"
            .format(len(customer.name), address_max_len))

        self.assertTrue(len(customer.comments) <= comments_max_len,
            "comments with length {}, does not respect max length restriction of {}"
            .format(len(customer.comments), comments_max_len))




    def test_default_with_max_length(self):
        faker = fake
        seeder = Seeder(faker)

        seeder.add_entity(Product, 1)

        _id = seeder.execute()

        product = Product.objects.get(id=_id[Product][0])

        self.assertTrue(len(DEF_LD) == len(product.description))

class RelationshipTestCase(TestCase):

    def test_one_to_one(self):
        faker = fake
        seeder = Seeder(faker)

        seeder.add_entity(Pen, 1)
        seeder.add_entity(Reporter, 1)

        result = seeder.execute()
        self.assertEqual(Reporter.objects.get(id=result[Reporter][0]).pen.pk, result[Pen][0])

    def test_one_to_one_wrong_order(self):
        faker = fake
        seeder = Seeder(faker)

        seeder.add_entity(Reporter, 1)
        seeder.add_entity(Pen, 1)

        self.assertRaises(SeederException, seeder.execute)

    def test_many_to_one(self):
        faker = fake
        seeder = Seeder(faker)

        seeder.add_entity(Pen, 1)
        seeder.add_entity(Reporter, 1)
        seeder.add_entity(Article, 1)

        results = seeder.execute()

        self.assertNotEqual(Reporter.objects.get(id=results[Reporter][0]), None)
        self.assertNotEqual(Article.objects.get(id=results[Article][0]), None)
        self.assertEqual(Article.objects.get(id=results[Article][0]).reporter.pk, results[Reporter][0])

    def test_many_to_one_wrong_order(self):
        faker = fake
        seeder = Seeder(faker)

        seeder.add_entity(Article, 1)
        seeder.add_entity(Pen, 1)
        seeder.add_entity(Reporter, 1)

        self.assertRaises(SeederException, seeder.execute)

    def test_many_to_many(self):
        faker = fake
        seeder = Seeder(faker)

        seeder.add_entity(Pen, 1)
        seeder.add_entity(Reporter, 1)
        seeder.add_entity(Article, 1)
        seeder.add_entity(Newspaper, 1)

        results = seeder.execute()
        self.assertNotEqual(Newspaper.objects.get(id=1), None)
        self.assertNotEqual(Reporter.objects.get(id=1), None)
        self.assertNotEqual(Article.objects.get(id=1), None)
        self.assertEqual(len(Reporter.objects.get(id=1).newspaper_set.all()), 1)

    # TODO: This test should work once
    # https://github.com/Brobin/django-seed/issues/79 is resolved

    # def test_many_to_many_separate_executes(self):
    #     faker = fake
    #     seeder = Seeder(faker)

    #     seeder.add_entity(Pen, 1)
    #     seeder.add_entity(Reporter, 1)
    #     seeder.add_entity(Article, 1)

    #     seeder.execute()

    #     seeder.add_entity(Newspaper, 1)

    #     seeder.execute()
    #     self.assertNotEqual(Newspaper.objects.get(id=1), None)
    #     self.assertNotEqual(Reporter.objects.get(id=1), None)
    #     self.assertNotEqual(Article.objects.get(id=1), None)
    #     self.assertEqual(len(Reporter.objects.get(id=1).newspaper_set.all()), 1)

class EdgeCaseFieldTestCase(TestCase):

    @skipIf(settings.DATABASES['default']['ENGINE'] != 'django.db.backends.postgresql_psycopg2', "Postgres database is not configured, or the tests aren't being run with the `actions` argument.")
    def test_postgres_array_field(self):
        print("Aasdf")
        faker = fake
        seeder = Seeder(faker)
        seeder.add_entity(NotCoveredFields, 1)

        seeder.execute()
