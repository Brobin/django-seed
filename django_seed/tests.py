from faker import Faker
from django_seed.seeder import Seeder
from django_seed import Faker as DjangoFaker

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

    def test_formatter(self):
        generator = fake

        seeder = Seeder(generator)

        seeder.add_entity(Game,5)
        seeder.add_entity(Player, 10, {
            'score': lambda x: random.randint(0,1000),
            'nickname': lambda x: fake.email()
        })
        seeder.add_entity(Action,30)

        insertedPks = seeder.execute()

        self.assertTrue(len(insertedPks[Game]) == 5)
        self.assertTrue(len(insertedPks[Player]) == 10)

        self.assertTrue(any([0 <= p.score <= 1000 and '@' in p.nickname for p in Player.objects.all() ]))


class APIDjangoFakerTestCase(unittest.TestCase):

    def test_django_seed_singleton(self):
        self.assertEqual(DjangoFaker() , DjangoFaker())
        self.assertIs(DjangoFaker() , DjangoFaker())

    def test_faker_cache_generator(self):
        self.assertEqual(DjangoFaker().generator(), DjangoFaker().generator())
        self.assertIs(DjangoFaker().generator(), DjangoFaker().generator())
        self.assertIs(DjangoFaker().generator(codename='default'), DjangoFaker().generator(codename='default'))

        self.assertEqual(DjangoFaker().generator(locale='it_IT'), DjangoFaker().generator(locale='it_IT'))
        self.assertIs(DjangoFaker().generator(locale='it_IT'), DjangoFaker().generator(locale='it_IT'))

    def test_faker_cache_seeder(self):
        self.assertEqual(DjangoFaker().seeder(), DjangoFaker().seeder())
        self.assertIs(DjangoFaker().seeder(), DjangoFaker().seeder())
        self.assertIs(DjangoFaker().seeder().generator, DjangoFaker().seeder().generator)

        self.assertEqual(DjangoFaker().seeder(locale='it_IT'), DjangoFaker().seeder(locale='it_IT'))
        self.assertIs(DjangoFaker().seeder(locale='it_IT'), DjangoFaker().seeder(locale='it_IT'))
        