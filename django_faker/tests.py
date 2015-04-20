from faker import Faker
from django_faker.populator import Populator
from django_faker import Faker as DjangoFaker

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


class PopulatorTestCase(unittest.TestCase):

    def testPopulation(self):

        generator = fake
        populator = Populator(generator)
        populator.addEntity( Game, 10 )
        self.assertEqual(len(populator.execute()[Game]), 10)

    def testGuesser(self):

        generator = fake

        def title_fake(arg):
            title_fake.count += 1
            name = generator.company()
            return name
        title_fake.count = 0

        populator = Populator(generator)
        populator.addEntity( Game, 10, {
            'title': title_fake
        } )
        self.assertEqual(len(populator.execute()[Game]), title_fake.count)

    def testFormatter(self):

        generator = fake

        populator = Populator( generator )

        populator.addEntity(Game,5)
        populator.addEntity(Player, 10, {
            'score': lambda x: fake.randomInt(0,1000),
            'nickname': lambda x: fake.email()
        })
        populator.addEntity(Action,30)

        insertedPks = populator.execute()

        self.assertTrue( len(insertedPks[Game]) == 5 )
        self.assertTrue( len(insertedPks[Player]) == 10 )

        self.assertTrue( any([0 <= p.score <= 1000 and '@' in p.nickname for p in Player.objects.all() ]) )


class APIDjangoFakerTestCase(unittest.TestCase):

    def testDjangoFakerSingleton(self):

        self.assertEqual( DjangoFaker() , DjangoFaker() )
        self.assertIs( DjangoFaker() , DjangoFaker() )

    def testFakerCacheGenerator(self):

        self.assertEqual( DjangoFaker().getGenerator(), DjangoFaker().getGenerator() )
        self.assertIs( DjangoFaker().getGenerator(), DjangoFaker().getGenerator() )
        self.assertIs( DjangoFaker().getGenerator(codename='default'), DjangoFaker().getGenerator(codename='default') )

        self.assertEqual( DjangoFaker().getGenerator(locale='it_IT'), DjangoFaker().getGenerator(locale='it_IT') )
        self.assertIs( DjangoFaker().getGenerator(locale='it_IT'), DjangoFaker().getGenerator(locale='it_IT') )

    def testFakerCachePopulator(self):

        self.assertEqual( DjangoFaker().getPopulator(), DjangoFaker().getPopulator() )
        self.assertIs( DjangoFaker().getPopulator(), DjangoFaker().getPopulator() )
        self.assertIs( DjangoFaker().getPopulator().generator, DjangoFaker().getPopulator().generator )

        self.assertEqual( DjangoFaker().getPopulator(locale='it_IT'), DjangoFaker().getPopulator(locale='it_IT') )
        self.assertIs( DjangoFaker().getPopulator(locale='it_IT'), DjangoFaker().getPopulator(locale='it_IT') )
        