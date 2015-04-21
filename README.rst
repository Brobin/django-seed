===========
Django-seed
===========

*Django-seed* uses the `faker`_ library to generate test data for your Django models. This has been forked from `django_faker`_ because it is no longer in development and does not have support for Python 3

Not only will this version allow you to write code to generate models, it will allow you to seed your database with one simple ``manage.py`` command!

---------------

|python| |travis| |license|

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

To install django-seed you can use pip::

    pip install git+https://github.com/brobin/django-seed.git


-------------
Configuration
-------------

In django application ``settings.py``::

    INSTALLED_APPS = (
        ...
        'django_seed',
    )

-----
Usage
-----

Using with command
------------------

One improvement that django-seed has over django-faker is the ability to seed your database from the command line. Using the ``manage.py seed`` command, you can do this automagically.

Ex] Seed 15 of each model for the app ``api``:

.. code-block:: bash

    $ python manage.py seed api --number=15
    
That's it! Now you have 15 of each model seeded into your database.


Using with code
----------------

*django-seed* provides methods to easily seed test databases for your Django models. To seed your database with Model instances, create a ``Seed`` instance and use the `add_entity` method.

Ex: seeding 5 ``Game`` and 10 ``Player`` objects:

.. code-block:: python

    from django_seed import Seed

    seeder = Seed.seeder()

    from myapp.models import Game, Player
    seeder.add_entity(Game, 5)
    seeder.add_entity(Player, 10)

    inserted_pks = seeder.execute()

The seeder uses the name and column type to populate the Model with relevant data. If django-seed misinterprets a column name, you can still specify a custom function to be used for populating a particular column, addming a third argument to ``add_entity()``:

.. code-block:: python

    seeder.add_entity(Player, 10, {
        'score':    lambda x: random.randint(0,1000),
        'nickname': lambda x: seeder.faker.email(),
    })
    seeder.execute()

Django-seed does not populate autoincremented primary keys, instead ``django_seed.seeder.Seeder.execute()`` returns the list of inserted PKs, indexed by class:

.. code-block:: python

    print inserted_pks
    {
        <class 'faker.django.tests.Player'>: [1, 2, 3, 4, 5, 6, 7, 8, 9, 10],
        <class 'faker.django.tests.Game'>: [1, 2, 3, 4, 5]
    }


-----
Tests
-----

Run django tests in a django environment:

.. code-block:: bash

    $ python runtests.py

or if you have ``django_seed`` in INSTALLED_APPS:

.. code-block:: bash

    $ python manage.py test django_seed
  

-------  
License
-------

MIT. See LICENSE for more details.


.. _faker: https://www.github.com/joke2k/faker/
.. _django_faker: https://www.github.com/joke2k/django-faker/

.. |travis| image:: https://img.shields.io/travis/Brobin/django-seed.svg?style=flat-square
    :target: http://travis-ci.org/Brobin/django-seed
    :alt: Travix Build

.. |license| image:: https://img.shields.io/github/license/Brobin/django-seed.svg?style=flat-square
    :target: https://github.com/Brobin/django-seed/blob/master/LICENSE
    :alt: MIT License

.. |python| image:: https://img.shields.io/badge/python-2.7, 3.x-blue.svg?style=flat-square
    :alt: Python 2.7, 3.x
