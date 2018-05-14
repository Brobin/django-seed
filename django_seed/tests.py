from contextlib import contextmanager
from datetime import datetime

from django.utils import timezone
from faker import Faker

from django_seed.guessers import NameGuesser, FieldTypeGuesser
from django_seed.seeder import Seeder
from django_seed.exceptions import SeederException, SeederCommandError
from django_seed import Seed

import random

from django.db import models
from django.conf import settings
from django.core.management import call_command

try:
    from django.utils.unittest import TestCase
except:
    from django.test import TestCase


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
    ip = models.IPAddressField()
    achievements = models.CommaSeparatedIntegerField(max_length=1000)
    friends = models.PositiveIntegerField()
    balance = models.FloatField()

class Action(models.Model):
    ACTION_FIRE ='fire'
    ACTION_MOVE ='move'
    ACTION_STOP ='stop'
    ACTIONS = (
        (ACTION_FIRE,'Fire'),
        (ACTION_MOVE,'Move'),
        (ACTION_STOP,'Stop'),
    )
    name = models.CharField(max_length=4, choices=ACTIONS)
    executed_at = models.DateTimeField()
    duration = models.DurationField()
    uuid = models.UUIDField()
    actor = models.ForeignKey(to=Player,on_delete=models.CASCADE,related_name='actions', null=False)
    target = models.ForeignKey(to=Player,on_delete=models.CASCADE, related_name='enemy_actions+', null=True)

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



class SeederTestCase(TestCase):

    def test_population(self):
        faker = fake
        seeder = Seeder(faker)
        seeder.add_entity(Game, 10)
        self.assertEqual(len(seeder.execute()[Game]), 10)

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
        seeder.add_entity(Game,5)
        seeder.add_entity(Player, 10, {
            'score': lambda x: random.randint(0,1000),
            'nickname': lambda x: fake.email()
        })
        seeder.add_entity(Action,30)
        inserted_pks = seeder.execute()
        self.assertTrue(len(inserted_pks[Game]) == 5)
        self.assertTrue(len(inserted_pks[Player]) == 10)

        players = Player.objects.all()
        self.assertTrue(any([self.valid_player(p) for p in players]))

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
        date =  datetime(1957, 3, 6, 13, 13)
        faker = fake
        seeder = Seeder(faker)
        seeder.add_entity(Game, 10, {
            'created_at': lambda x: date
        })
        inserted_pks = seeder.execute()[Game]

        games = Game.objects.filter(pk__in=inserted_pks)
        self.assertTrue(all(game.created_at == date for game in games))

    def test_auto_now(self):
        date =  datetime(1957, 3, 6, 13, 13)
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


