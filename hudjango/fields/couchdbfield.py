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

from urlparse import urljoin


####################################################
# put somewhere else...
from django import forms
from django.utils.safestring import mark_safe

class CouchDBWidget(forms.widgets.Widget):
    def render(self, name, value, attrs=None):
        return mark_safe(u'<input size="64" name="%s" value="%s" />' % (name, value))

class CouchDBFormField(forms.Field):
    #widget = CouchDBWidget
    def __init__(self, *args, **kwargs):
        super(CouchDBFormField, self).__init__(*args, **kwargs)
        self.widget = CouchDBWidget()
####################################################


class CouchDBDocument(couchdb.client.Document):
    """CouchDBDocument"""
    
    def __unicode__(self):
        return urljoin(self.server, '%s/%s' % (self.database, self.id))
    
    def set_location(self, server, database):
        self.server = server
        self.database = database
    
    def get_location(self):
        return self.server, self.database, self.id
    
    def save(self):
        """
        Save document to CouchDB.
        
        If the document exists already, get previous revision and update document
        """
        
        if not (hasattr(self, 'server') or hasattr(self, 'database')):
            raise RuntimeError("object has not been told where to save!")
        
        couchdb =  setup_couchdb(self.server, self.database)
        if self.id in couchdb:
            doc = couchdb[self.id]
            self.update(doc)
        couchdb[self.id] = self


class CouchDBField(models.CharField):

    description = "Store id of a CouchDB document"
    
    __metaclass__ = models.SubfieldBase
    
    def __init__(self, server=None, database=None, **kwargs):
        self.server, self.database = server, database
        self._couchcon = None
        
        # Keep track of CouchDB document id to prevent creation of new documents
        self.doc_id = None
        kwargs['max_length'] = 256
        
        super(CouchDBField, self).__init__(**kwargs)
    
    def _connection(self, server=None, database=None):
        """Cache connection to CouchDB"""
        if self._couchcon is None:
            self._couchcon = setup_couchdb(server, database)
        return self._couchcon
    
    def to_python(self, value):
        """Convert to Python object"""
        
        if value == '' or value is None:
            doc = CouchDBDocument()
        elif isinstance(value, dict):
            doc = CouchDBDocument(_id=self.doc_id, **value)
        else:
            try:
                server, database, doc_id = value.split('#')
                doc = CouchDBDocument(self._connection(server, database)[doc_id])
            except:
                print "ui!"
                doc = CouchDBDocument()
        doc.set_location(self.server, self.database)
        return doc
    
    def get_db_prep_value(self, value):
        """Convert Python object to database value"""
        return "#".join(value.get_location())
    
    def get_db_prep_save(self, value):
        """
        Save document to CouchDB when saving Django object.
        
        If it's a new document, generate an id.
        """
        
        if (not '_id' in value) or (value.get('_id') is None):
            value['_id'] = uuid4().hex
            self.doc_id = value['_id']
        value.save()
        return self.get_db_prep_value(value)
    
    def contribute_to_class(self, cls, name):
        super(CouchDBField, self).contribute_to_class(cls, name)
        models.signals.post_delete.connect(self.delete, sender=cls)
    
    def delete(self, **kwargs):
        """Delete the document from the CouchDB database."""
        if self.doc_id:
            doc = self._connection(self.server, self.database)[self.doc_id]
            self._connection(self.server, self.database).delete(doc)
    
    def formfield(self, form_class=CouchDBFormField, **kwargs):
        defaults = {'required': not self.blank, 'label': self.verbose_name, 'help_text': self.help_text}
        defaults.update(kwargs)
        return form_class(**defaults)
