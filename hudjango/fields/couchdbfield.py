#!/usr/bin/env python
# encoding: utf-8

"""
couchdbfield.py

Django field for storing information about a CouchDB document

Created by Christian Klein on 2010-02-24.
(c) 2010 HUDORA GmbH. All rights reserved.
"""

from django.db import models
import couchdb.client
from uuid import uuid4
from huTools.couch import setup_couchdb


class CouchDBDocument(couchdb.client.Document):
    """CouchDBDocument"""
    
    def __init__(self, *args, **kwargs):
        
        try:
            self.server = kwargs['server']
            del kwargs['server']
            self.database = kwargs['database']
            del kwargs['database']
        except IndexError:
            raise ValueError('server and database must not be None')
        
        super(CouchDBDocument, self).__init__(*args, **kwargs)

    def get_location(self):
        return self.server, self.database, self.id

    def save(self):
        """Save document to CouchDB"""
        couchdb =  setup_couchdb(self.server, self.database)
	couchdb[self.id] = self


class CouchDBField(models.CharField):

    description = "Store id of a CouchDB document"
    
    __metaclass__ = models.SubfieldBase

    def __init__(self, server=None, database=None, **kwargs):
        self.server = server
        self.database = database
        self._couchcon = None
        kwargs['max_length'] = 256
                
        super(CouchDBField, self).__init__(**kwargs)

    def _connection(self, server, database=None):
        """Cache connection to CouchDB"""
        if self._couchcon is None:
            self._couchcon = setup_couchdb(server, database)
        return self._couchcon

    def to_python(self, value):
        """Convert to Python object"""
        if value == '' or value is None:
            return CouchDBDocument(server=self.server, database=self.database)
        server, database, doc_id = value.split('#')
	try:
	    doc = CouchDBDocument(self._connection(server, database)[doc_id],
                                  server=server, database=database)
	except couchdb.client.ResourceNotFound:
            doc = None
        return doc

    def get_db_prep_value(self, value):
        """Convert Python object to database value"""
        return "#".join(value.get_location())
    
    def get_db_prep_save(self, value):
        """Save document to CouchDB when saving Django object"""
        
        if not '_id' in value:
            value['_id'] = uuid4().hex
        value.save()
        #server, database, doc_id = value.get_location()
        #self._connection(server)[database][doc_id] = value
        return self.get_db_prep_value(value)
