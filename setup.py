long_description = """
huDjango contains a collection of small extensions th the Django Web framework.

auth.backends.EmailBackend - authentication with E-Mail adress
auth.backends.ZimbraBackend - authentication against a Zimbra LDAP server
hudjango.fields.scalingimagefield - images with automatic scaling
hudjango.fields.defaulting - Django fields with more elaborate default values.
hudjango.fields.audit - Django fields with store user & IP.
middleware.threadlocals - Thread local storage.
"""

from ez_setup import use_setuptools
use_setuptools()
from setuptools import setup, find_packages

# patch distutils if it can't cope with the "classifiers" or
# "download_url" keywords
from sys import version
if version < '2.2.3':
    from distutils.dist import DistributionMetadata
    DistributionMetadata.classifiers = None
    DistributionMetadata.download_url = None
            
hubarcode = setup(name='huDjango',
      maintainer='Maximillian Dornseif',
      maintainer_email='md@hudora.de',
      url='https://cybernetics.hudora.biz/projects/wiki/huDjango',
      version='0.72',
      description='various snippets for use with Django',
      long_description=long_description,
      classifiers=['License :: OSI Approved :: BSD License',
                   'Intended Audience :: Developers',
                   'Programming Language :: Python'],
      # download_url
      #packages=['hudjango'],
      packages = find_packages(),
)

