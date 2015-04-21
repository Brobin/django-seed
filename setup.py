import os
from setuptools import setup

setup(
    name='django-seed',
    version=__import__('django_seed').__version__,
    author='Tobin Brown',
    author_email='tobin@brobin.me',
    packages=['django_seed'],
    include_package_data=True,
    url='http://github.com/brobin/django-seed',
    license='MIT',
    description='Seed your Django projcet with fake data',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Information Technology',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 3',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Topic :: Software Development :: Testing',
        'Topic :: Software Development :: Widget Sets',
        'Topic :: Utilities',
        'License :: OSI Approved :: MIT License',
        'Framework :: Django'
    ],
    keywords='faker fixtures data test django',
    long_description=open('README.rst', 'r').read(),
    install_requires=['django>=1.7','fake-factory>=0.5.0'],
    tests_require=['django>=1.7','fake-factory>=0.5.0'],
    test_suite="runtests.runtests",
    zip_safe=False,
)
