|seed-logo|

===========

*Django-seed* uses the `faker`_ library to generate test data for your Django models. This has been "hard-forked" from `django_faker`_ in order to support newer versions of Python and Django

Django-seed allows you to write code to generate models, and seed your database with one simple ``manage.py`` command!

---------------

|python| |pypi| |actions| |coveralls| |license| |downloads|

---------------

* `Installation`_
* `Configuration`_
* `Usage`_
* `Using with command`_
* `Using with code`_
* `Tests`_
* `License`_

---------------

------------
Installation
------------

To install django-seed, use pip::

    pip install django-seed

Or to install from source::

    python setup.py install


-------------
Configuration
-------------

Add it to your installed apps in ``settings.py``::

    INSTALLED_APPS = (
        ...
        'django_seed',
    )

-----
Usage
-----

**Note**: When seeding models with Foreign Keys, you need to make sure that those models are seeded first. For example, if a model in app `A` has a foreign key to a model in app `B`, you must seed app `B` first.

Using with command
------------------

With *django-seed*, you can seed your database with test data from the command line using the ``manage.py seed`` command.

Ex: Seed 15 of each model for the app ``api``:

.. code-block:: bash

    $ python manage.py seed api --number=15

That's it! Now you have 15 of each model seeded into your database.

Should you need, you can also specify what value a particular field should have. For example, if you want to seed 15 of ``MyModel``, but you need ``my_field`` to be the same on all of them, you can do it like this: 

.. code-block:: bash

    $ python manage.py seed api --number=15 --seeder "MyModel.my_field" "1.1.1.1"
    
This is the command equivalent to doing it in Python:

.. code-block:: python

    seeder.add_entity(MyModel, 10, {
        'my_field': '1.1.1.1',
    })

Using with code
----------------

*django-seed* provides methods to easily seed test databases for your Django models. To seed your database with Model instances, import ``Seed``, get a ``seeder`` instance, and use the `add_entity` method.

Ex: seeding 5 ``Game`` and 10 ``Player`` objects:

.. code-block:: python

    from django_seed import Seed

    seeder = Seed.seeder()

    from myapp.models import Game, Player
    seeder.add_entity(Game, 5)
    seeder.add_entity(Player, 10)

    inserted_pks = seeder.execute()

The seeder uses the name and column type to populate the Model with relevant data. If django-seed misinterprets a column name or column type and *AttributeError(field)* is thrown, you can still specify a custom function to be used for populating a particular column, by adding a third argument to the ``add_entity()`` method:

.. code-block:: python

    seeder.add_entity(Player, 10, {
        'score':    lambda x: random.randint(0, 1000),
        'nickname': lambda x: seeder.faker.email(),
    })
    seeder.execute()

Django-seed does not populate auto-incremented primary keys, instead ``seeder.execute()`` returns the list of inserted PKs, indexed by class:

.. code-block:: python

    print inserted_pks
    {
        <class 'faker.django.tests.Player'>: [1, 2, 3, 4, 5, 6, 7, 8, 9, 10],
        <class 'faker.django.tests.Game'>: [1, 2, 3, 4, 5]
    }

You may specify a different locale by passing it in the constructor of the seeder. Defaults to `settings.LANGUAGE_CODE`

.. code-block:: python

    seeder = Seed.seeder(locale='sv_SE')
    seeder.faker.city()  # 'Västerås'


Localization
------------

``Seed.seeder()`` can take a locale as an argument, to return localized data.
You can find all possible locales in `faker's documentation`_

In order to apply localization, do the next:

.. code-block:: python

    seeder = Seed.seeder('it_IT')

-----
Tests
-----

To run django tests in a django environment, first make sure you have the packages from `requirement-test.txt` installed, then run the following:

.. code-block:: bash

    $ python runtests.py

or if you have ``django_seed`` in INSTALLED_APPS:

.. code-block:: bash

    $ python manage.py test django_seed

-------
License
-------

MIT. See `LICENSE`_ for more details.


.. _faker: https://www.github.com/joke2k/faker/
.. _django_faker: https://www.github.com/joke2k/django-faker/
.. _faker's documentation: https://faker.readthedocs.io/en/latest/locales.html
.. _LICENSE: https://github.com/Brobin/django-seed/blob/master/LICENSE

.. |pypi| image:: https://img.shields.io/pypi/v/django-seed.svg?style=flat-square
    :target: https://pypi.python.org/pypi/django-seed
    :alt: pypi

.. |actions| image:: https://github.com/Brobin/django-seed/workflows/Test/badge.svg
    :target: https://github.com/Brobin/django-seed
    :alt: Actions Build
    
.. |coveralls| image:: https://img.shields.io/coveralls/Brobin/django-seed.svg?style=flat-square
    :target: https://coveralls.io/r/Brobin/django-seed
    :alt: coverage

.. |license| image:: https://img.shields.io/github/license/Brobin/django-seed.svg?style=flat-square
    :target: https://github.com/Brobin/django-seed/blob/master/LICENSE
    :alt: MIT License

.. |python| image:: https://img.shields.io/pypi/pyversions/django-seed.svg?style=flat-square
    :target: https://pypi.python.org/pypi/django-seed
    :alt: Python 3.x

.. |seed-logo| image:: assets/django_seed.png
    :alt: Django Seed

.. |downloads| image:: https://pepy.tech/badge/django-seed
    :target: https://pepy.tech/project/django-seed
    :alt: downloads
