import os
from setuptools import setup, find_packages


def read_file(filename):
    """Read a file into a string"""
    path = os.path.abspath(os.path.dirname(__file__))
    filepath = os.path.join(path, filename)
    try:
        return open(filepath).read()
    except IOError:
        return ''


setup(
    name='django-faker',
    version=__import__('django_faker').__version__,
    author='joke2k',
    author_email='joke2k@gmail.com',
    packages=find_packages(),
    include_package_data=True,
    url='http://github.com/joke2k/django-faker',
    license='MIT',
    description=u' '.join(__import__('django_faker').__doc__.splitlines()).strip(),
    classifiers=[
        # Get strings from http://pypi.python.org/pypi?%3Aaction=list_classifiers
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
    long_description=read_file('README.rst'),
    install_requires=['django','faker>=0.2'],
    tests_require=['django','faker>=0.2'],
    test_suite="runtests.runtests",
    zip_safe=False,
)