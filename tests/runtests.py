#!/usr/bin/env python

import figleaf
figleaf.start(ignore_python_lib=True)

import doctest
import os
import sys
import traceback
import unittest

REGRESSION_TESTS_DIR_NAME = 'regressiontests'

TEST_TEMPLATE_DIR = 'templates'

REGRESSION_TEST_DIR = os.path.join(os.path.dirname(__file__), REGRESSION_TESTS_DIR_NAME)

ALWAYS_INSTALLED_APPS = [
    'django.contrib.contenttypes',
    'django.contrib.auth',
    'django.contrib.sites',
    #'django.contrib.flatpages',
    #'django.contrib.redirects',
    'django.contrib.sessions',
    #'django.contrib.comments',
    'django.contrib.admin',
]


def get_test_models():
    models = []
    for loc, dirpath in [(REGRESSION_TESTS_DIR_NAME, REGRESSION_TEST_DIR), ]:
        for f in os.listdir(dirpath):
            if f.startswith('__init__') or f.startswith('.') or f.startswith('sql') \
                or f.startswith('invalid') or f.endswith('.py') or f.endswith('.pyc'):
                continue
            models.append((loc, f))
    return models
    

def django_tests(verbosity, interactive, test_labels):
    from django.conf import settings
    
    old_installed_apps = settings.INSTALLED_APPS
    old_test_database_name = settings.TEST_DATABASE_NAME
    old_root_urlconf = settings.ROOT_URLCONF
    old_template_dirs = settings.TEMPLATE_DIRS
    old_use_i18n = settings.USE_I18N
    old_login_url = settings.LOGIN_URL
    old_language_code = settings.LANGUAGE_CODE
    old_middleware_classes = settings.MIDDLEWARE_CLASSES

    # Redirect some settings for the duration of these tests.
    settings.INSTALLED_APPS = ALWAYS_INSTALLED_APPS
    settings.ROOT_URLCONF = 'urls'
    settings.TEMPLATE_DIRS = (os.path.join(os.path.dirname(__file__), TEST_TEMPLATE_DIR), )
    settings.USE_I18N = True
    settings.LANGUAGE_CODE = 'en'
    settings.LOGIN_URL = '/accounts/login/'
    settings.MIDDLEWARE_CLASSES = (
        'django.contrib.sessions.middleware.SessionMiddleware',
        'django.contrib.auth.middleware.AuthenticationMiddleware',
        'django.middleware.common.CommonMiddleware',
    )
    settings.SITE_ID = 1

    # Load all the ALWAYS_INSTALLED_APPS.
    # (This import statement is intentionally delayed until after we
    # access settings because of the USE_I18N dependency.)
    from django.db.models.loading import get_apps, load_app
    get_apps()

    # Load all the test model apps.
    test_models = []
    for model_dir, model_name in get_test_models():
        model_label = '.'.join([model_dir, model_name])
        try:
            # if the model was named on the command line, or
            # no models were named (i.e., run all), import
            # this model and add it to the list to test.
            if not test_labels or model_name in set([label.split('.')[0] for label in test_labels]):
                if verbosity >= 1:
                    print "Importing model %s" % model_name
                mod = load_app(model_label)
                if mod:
                    if model_label not in settings.INSTALLED_APPS:
                        settings.INSTALLED_APPS.append(model_label)
        except Exception, e:
            sys.stderr.write("Error while importing %s:" % model_name + ''.join(traceback.format_exception(*sys.exc_info())[1:]))
            continue
    
    # Run the test suite, including the extra validation tests.
    from django.test.simple import run_tests
    failures = run_tests(test_labels, verbosity=verbosity, interactive=interactive)
    # now test docstrings in modules directly without the test runner
    for name, mod in sys.modules.items():
        if name.startswith('hudjango'):
            failure_count, test_count = doctest.testmod(mod)
            failures += failure_count
    
    if failures:
        sys.exit(failures)
    
    # Restore the old settings.
    settings.INSTALLED_APPS = old_installed_apps
    settings.ROOT_URLCONF = old_root_urlconf
    settings.TEMPLATE_DIRS = old_template_dirs
    settings.USE_I18N = old_use_i18n
    settings.LANGUAGE_CODE = old_language_code
    settings.LOGIN_URL = old_login_url
    settings.MIDDLEWARE_CLASSES = old_middleware_classes
    

if __name__ == "__main__":
    from optparse import OptionParser
    usage = "%prog [options] [model model model ...]"
    parser = OptionParser(usage=usage)
    parser.add_option('-v', '--verbosity', action='store', dest='verbosity', default='0',
        type='choice', choices=['0', '1', '2'],
        help='Verbosity level; 0=minimal output, 1=normal output, 2=all output')
    parser.add_option('--noinput', action='store_false', dest='interactive', default=True,
        help='Tells Django to NOT prompt the user for input of any kind.')
    parser.add_option('--settings',
        help='Python path to settings module, e.g. "myproject.settings". If this isn\'t provided, the DJANGO_SETTINGS_MODULE environment variable will be used.')
    options, args = parser.parse_args()
    if options.settings:
        os.environ['DJANGO_SETTINGS_MODULE'] = options.settings
    elif "DJANGO_SETTINGS_MODULE" not in os.environ:
        parser.error("DJANGO_SETTINGS_MODULE is not set in the environment. "
                      "Set it or use --settings.")
    django_tests(int(options.verbosity), options.interactive, args)
    figleaf.stop()
    figleaf.write_coverage('.figleaf', append=True)
