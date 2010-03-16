"""
Wrapper for loading templates from a CouchDB.
"""

from django.conf import settings
from django.template import TemplateDoesNotExist
from django.utils._os import safe_join

from urlparse import urljoin
import logging


def _setup_couchdb(servername, database):
    """Get a connection handler to the CouchDB Database, creating it when needed."""
    
    server = couchdb.client.Server(servername)
    if database in server:
        return server[database]
    else:
        return server.create(database)


try:
    from huTools.couch import setup_couchdb
except ImportError:
    import couchdb.client
    import warnings
    warnings.warn("Your huTools installation does not contain the couch module.", warnings.ImportWarning)
    setup_couchdb = _setup_couchdb


def load_template_source(template_name, template_dirs=None):
    
    if not hasattr(settings, 'TEMPLATE_COUCHDB_SERVER'):
        error_msg = "CouchDB Template Loader not configured"
        raise TemplateDoesNotExist, error_msg
    
    server = settings.TEMPLATE_COUCHDB_SERVER
    databasename = getattr(settings, 'TEMPLATE_COUCHDB_DATABASE', 'templates')
    database = setup_couchdb(server, databasename)
    
    if template_name in database:
        doc = database[template_name]
        try:
            template = doc['source']
            return template, urljoin(server, databasename, template_name)
        except KeyError:
            error_msg = "Document does not contain template code"
    else:
        error_msg = "No template '%s' found" % template_name
    raise TemplateDoesNotExist, error_msg
load_template_source.is_usable = True
