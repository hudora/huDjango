# encoding: utf-8
"""

Dynamically collect information about Django applications.

Example:

Define your "plugin" directory:
djangoprojectdir/apps/


"""


import os
import stat

def get_plugins(basedir):
    """
    Get a list of module names that represent Django applications.
    
    A file is considered a Django application if it's a symlink in your plugin base directory,
    is a Python package and contains a models.py
    """
    apps = []
    for filename in os.listdir(basedir):
        if stat.S_ISLNK(os.lstat(os.path.join(basedir, filename)).st_mode):
            # try to import file as a python module
            try:
                mod = __import__(filename)
            except:
                continue
            
            # the Django test framework requires a models.py for every application
            if os.path.exists(os.path.join(basedir, filename, 'models.py')):
                apps.append(filename)

    return apps


def get_plugins2(basedir):
    """
    Get a list of Django applications
    
    This works a little bit more like INSTALLED_APPS in settings.py:
    The app is represented by the filename in the plugin directory.
    """
    apps = []
    for filename in os.listdir(basedir):
        if stat.S_ISREG(os.stat(os.path.join(basedir, filename)).st_mode):
            apps.append(filename)

    return apps


def settings(basedir):
    """
    Return a tuple of Django applications that can be used in settings.py
    as an extension to INSTALLED_APPS
    """
    return tuple(get_plugins(basedir))


def urls(basedir):
    """
    Create a url pattern list.
    
    For every application abc in basedir, a RegexURLPattern is created like the following:
    url(r'^abc/', include('abc.urls'))
    """

    from django.conf.urls.defaults import patterns, include, url
    apps = []
    for app in get_plugins(basedir):
         apps.append(url(r'^%s/' % app, include('%s.urls' % app)))
    return patterns('', *apps)
