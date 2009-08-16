long_description = """
huDjango contains a collection of small extensions th the Django Web framework.

 * auth.backends.EmailBackend - authentication with E-Mail adress
 * auth.backends.ZimbraBackend - authentication against a Zimbra LDAP server
 * fields.scalingimagefield - images with automatic scaling
 * fields.defaulting - Django fields with more elaborate default values
 * templatetags.hudjango - Various template tags to make life more fun.
 * middleware.threadlocals - Thread local storage
 * validators - some simple validators
"""

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
      version='0.85p3',
      description='various snippets for use with Django',
      long_description=long_description,
      classifiers=['License :: OSI Approved :: BSD License',
                   'Intended Audience :: Developers',
                   'Programming Language :: Python'],
      zip_safe=True,
      packages=find_packages(),
      install_requires=['Django>=1.0.2', 'huimages>=1.01', 'textile', 'python-ldap'],
      dependency_links = ['http://cybernetics.hudora.biz/dist/',
                          'http://cybernetics.hudora.biz/nonpublic/eggs/'],
)

