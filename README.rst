Django-seed
============

*Django-seed* uses the `faker`_ to generate test data for your Django models. This has been forked from `django_faker`_ because it is no longer in development and does not have support for Python 3

How to use
----------

To install Django-faker you can use pip::

    pip install git+https://github.com/brobin/django-seed.git


Configuration
~~~~~~~~~~~~~

In django application `settings.py`::

    INSTALLED_APPS = (

        # ...
        'django_seed',
    )


Seeding Django Models
~~~~~~~~~~~~~~~~~~~~~~~~

*Django-faker* provides an adapter for Django Models, for easy population of test databases.
To populate with Model instances, create a new Populator class,
then list the class and number of all of Models that must be generated. To launch the actual data population,
call `execute()` method.

Here is an example showing how to populate 5 `Game` and 10 `Player` objects::

    from django_faker import Faker
    # this Populator is only a function thats return a django_faker.populator.Populator instance
    # correctly initialized with a faker.generator.Generator instance, configured as above
    populator = Faker.getPopulator()

    from myapp.models import Game, Player
    populator.add_entity(Game,5)
    populator.add_entity(Player,10)

    inserted_pks = populator.execute()

The populator uses name and column type guessers to populate each column with relevant data.
For instance, Django-faker populates a column named `first_name` using the `firstName` formatter, and a column with
a `datetime` instance using the `dateTime`.
The resulting entities are therefore coherent. If Django-faker misinterprets a column name, you can still specify a custom
function to be used for populating a particular column, using the third argument to `addEntity()`::


    populator.add_entity(Player, 10, {
        'score':    lambda x: random.randint(0,1000),
        'nickname': lambda x: populator.generator.email(),
    })
    populator.execute()

Of course, Django-faker does not populate autoincremented primary keys.
In addition, `django_faker.populator.Populator.execute()` returns the list of inserted PKs, indexed by class::

    print insertedPks
    {
        <class 'faker.django.tests.Player'>: [1, 2, 3, 4, 5, 6, 7, 8, 9, 10],
        <class 'faker.django.tests.Game'>: [1, 2, 3, 4, 5]
    }

In the previous example, the `Player` and `Game` models share a relationship. Since `Game` entities are populated first,
Faker is smart enough to relate the populated `Player` entities to one of populated `Game` entities.


Running the Tests
-----------------

Run django tests in a django environment:

    $ python runtests.py

or if you have 'django_faker' in INSTALLED_APPS:

    $ python manage.py test django_faker


.. _faker: https://www.github.com/joke2k/faker/
.. _django_faker: https://www.github.com/joke2k/django-faker/