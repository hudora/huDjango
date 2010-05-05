"""huDjango contains a collection of small extensions the the Django Web framework."""

import codecs
from setuptools import setup, find_packages

hubarcode = setup(name='huDjango',
      maintainer='Maximillian Dornseif',
      maintainer_email='md@hudora.de',
      url='http://github.com/hudora/huDjango',
      version='0.91p1',
      description='various snippets for use with Django',
      long_description=codecs.open('README.textile', "r", "utf-8").read(),
      classifiers=['License :: OSI Approved :: BSD License',
                   'Intended Audience :: Developers',
                   'Programming Language :: Python'],
      zip_safe=False,
      packages=find_packages(),
      install_requires=['Django>=1.0.2', 'huimages>=1.01', 'django-storages',
                        'textile', 'markdown', 'xlwt',
                        'docutils', 'CouchDB>=0.6.1', 'python-memcached'],
)
