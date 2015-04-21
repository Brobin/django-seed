from faker import Faker
from django_seed.seeder import Seeder
from django_seed import Faker as DjangoSeeder

import random

from django.db import models
from django.utils import unittest
from django.template import Context, TemplateSyntaxError
from django.template import Template


fake = Faker()


class Game(models.Model):

    title= models.CharField(max_length=200)
    slug= models.SlugField(max_length=200)
    description= models.TextField()
    created_at= models.DateTimeField()
    updated_date= models.DateField()
    updated_time= models.TimeField()
    active= models.BooleanField()
    max_score= models.BigIntegerField()


class Player(models.Model):

    nickname= models.CharField(max_length=100)
    score= models.BigIntegerField()
    last_login_at= models.DateTimeField()

    game= models.ForeignKey(Game)


class Action(models.Model):
    ACTION_FIRE='fire'
    ACTION_MOVE='move'
    ACTION_STOP='stop'

    ACTIONS = (
        (ACTION_FIRE,'Fire'),
        (ACTION_MOVE,'Move'),
        (ACTION_STOP,'Stop'),
   )

    name= models.CharField(max_length=4, choices=ACTIONS)
    executed_at= models.DateTimeField()
    actor= models.ForeignKey(Player,related_name='actions', null=True)
    target= models.ForeignKey(Player, related_name='enemy_actions+', null=True)


class SeederTestCase(unittest.TestCase):

    def test_population(self):
        generator = fake
        seeder = Seeder(generator)
        seeder.add_entity(Game, 10)
        self.assertEqual(len(seeder.execute()[Game]), 10)

    def test_guesser(self):
        generator = fake

        def title_fake(arg):
            title_fake.count += 1
            name = generator.company()
            return name
        title_fake.count = 0

        seeder = Seeder(generator)
        seeder.add_entity(Game, 10, {
            'title': title_fake
        })
        self.assertEqual(len(seeder.execute()[Game]), title_fake.count)

    def valid_player(self, player):
        p = player
        return 0 <= p.score <= 1000 and '@' in p.nickname

    def test_formatter(self):
        generator = fake

        seeder = Seeder(generator)

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


class APIDjangoSeederTestCase(unittest.TestCase):

    def setUp(self):
        self.seed1 = DjangoSeeder()
        self.seed2 = DjangoSeeder()

    def test_django_seed_singleton(self):
        self.assertEqual(self.seed1, self.seed2)
        self.assertIs(self.seed1, self.seed1)

    def test_faker_cache_generator(self):
        gen1 = self.seed1.generator()
        gen2 = self.seed2.generator()
        self.assertIs(gen1, gen2)

        gen1 = self.seed1.generator(codename='default')
        gen2 = self.seed2.generator(codename='default')
        self.assertIs(gen1, gen2)

        gen1 = self.seed1.generator(locale='it_IT')
        gen2 = self.seed2.generator(locale='it_IT')
        self.assertIs(gen1, gen2)

    def test_faker_cache_seeder(self):
        seeder1 = self.seed1.seeder()
        seeder2 = self.seed2.seeder()
        self.assertIs(seeder1, seeder2)

        gen1 = seeder1.generator
        gen2 = seeder2.generator
        self.assertIs(gen1, gen2)

        seeder1 = self.seed1.seeder(locale='it_IT')
        seeder2 = self.seed2.seeder(locale='it_IT')
        self.assertIs(seeder1, seeder2)
        