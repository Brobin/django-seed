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


class TemplateTagsTestCase(unittest.TestCase):

    @staticmethod
    def render( template, context=None ):
        t = Template("{% load fakers %}"+template)
        c = Context(context or {})
        text=  t.render(c)
        return text

    # do_fake: fake
    def testSimpleFakeTag(self):
        self.assertNotEqual(self.render("{% fake 'name' as myname %}{{ myname }}"),"")

    def testSimpleFakeTagWithArguments(self):
        self.assertNotEqual(self.render("{% fake 'dateTimeBetween' '-10d' as mydate %}{{ mydate }}"),"")

    def testSimpleFakeTagFormatterNotFoundRaisesException(self):
        with self.assertRaises(AttributeError):
            self.render("{% fake 'notFoundedFake' as foo %}")

    def testSimpleFakeTagOptionalAssignment(self):
        self.assertNotEqual(self.render("{% fake 'name' %}"),"")
        self.assertEqual(len(self.render("{% fake 'md5' %}")),32)

    # do_fake_filter: fake
    def testFakeFilterTag(self):
        self.assertIn(self.render("{{ 'randomElement'|fake:'testString' }}"),'testString')

    def testFakeFilterWithValueFromContext(self):
        mylist = [100,200,300]
        rendered = self.render("{{ 'randomElement'|fake:mylist }}", {'mylist': mylist})
        self.assertIn(rendered, [unicode(el) for el in mylist])

    def testFakeFilterFormatterNotFoundRaisesException(self):
        with self.assertRaises(AttributeError):
            self.render("{{ 'notFoundedFake'|fake:mylist }}", {'mylist': [100,200,300]})

    def testFakeFilterAsIfCondition(self):
        self.assertEqual(self.render("{% if 'boolean'|fake:100 %}True forever{% endif %}"), "True forever")
        self.assertEqual(self.render("{% if 'boolean'|fake:0 %}{% else %}False forever{% endif %}"), "False forever")

    def testFakeFilterAsForInRange(self):
        times = 10
        rendered = self.render("{% for word in 'words'|fake:times %}{{ word }}\n{% endfor %}",{'times':times})
        words = [word for word in rendered.split('\n') if word.strip()]
        self.assertEqual( len(words) , times)

    # do_or_fake_filter: or_fake
    def testOrFakeFilterTag(self):
        self.assertEqual(len(self.render("{{ unknown_var|or_fake:'md5' }}")), 32)


    def testFullXmlContact(self):
        self.assertTrue(self.render("""<?xml version="1.0" encoding="UTF-8"?>
<contacts>
    {% fake 'randomInt' 10 20 as times %}
    {% for i in 10|get_range %}
    <contact firstName="{% fake 'firstName' %}" lastName="{% fake 'lastName' %}" email="{% fake 'email' %}"/>
        <phone number="{% fake 'phoneNumber' %}"/>
        {% if 'boolean'|fake:25 %}
        <birth date="{{ 'dateTimeThisCentury'|fake|date:"D d M Y" }}" place="{% fake 'city' %}"/>
        {% endif %}
        <address>
            <street>{% fake 'streetAddress' %}</street>
            <city>{% fake 'city' %}</city>
            <postcode>{% fake 'postcode' %}</postcode>
            <state>{% fake 'state' %}</state>
        </address>
        <company name="{% fake 'company' %}" catchPhrase="{% fake 'catchPhrase' %}">
        {% if 'boolean'|fake:25 %}
            <offer>{% fake 'bs' %}</offer>
        {% endif %}
        {% if 'boolean'|fake:33 %}
            <director name="{% fake 'name' %}" />
        {% endif %}
        </company>
        {% if 'boolean'|fake:15 %}
        <details>
        <![CDATA[
        {% fake 'text' 500 %}
        ]]>
        </details>
        {% endif %}
    </contact>
    {% endfor %}
</contacts>
"""))


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
        