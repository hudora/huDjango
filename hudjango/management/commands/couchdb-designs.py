# -*- coding: utf8 -*-

from optparse import make_option
from hudjango.management.couchdb.support import CouchDBBaseCommand
from django.core.management.base import CommandError
import couchdb
import re
import os


class Command(CouchDBBaseCommand):

    help = re.sub(r'\n\s*','\n',"""
        Create and insert all design documents into the database. Existing design
        documents will be overwritten with new revisions.
    """)

    def handle(self, *args, **options):
        functions = self.load_document_parts(self._documents_path(options))
        docs = self.create_documents(functions)
        try: 
            self.upload_documents(self._db(options), docs)
        except couchdb.client.ResourceNotFound:
            print "The database you're trying to access doesn't exist!"

    def upload_documents(self, db, documents):
        """ push the design documents into the CouchDB server """
        for doc in documents:
            id = doc['_id']
            existing = db.get(id)
            if existing:
                doc['_rev']=existing['_rev']
            db[id] = doc
            print "successfully inserted design '%s'" % id

    def create_documents(self, functions):
        """ convert the collected javascript function snippets into CouchDB 
            design documents. The method returns the generated design docs """

        docs = []
        for name in functions.keys():
            doc = { '_id': '_design/%s' % name,
                    'language': 'javascript',
                    'views': {}
                  }
            view_cnt = 0
            for view in functions[name].keys():
                if len(functions[name][view])>0:
                    doc['views'][view]=functions[name][view]
                    view_cnt += 1
            if view_cnt>0:
                docs.append(doc)
        return docs

    def load_document_parts(self, documents_path):
        """ traverses the path containing the CouchDB design documents to collect
            the list of map/ reduce files. The method returns a directory of 
            design documents with its corresponding javascript definitions. """

        documents = {}
        for root, dirs, files in os.walk(documents_path, topdown=True):
            for name in dirs:
                documents[name] = {}
            for name in files:
                parts = re.match(r'([\w\-_]+)-(map|reduce)\.js', name)
                if parts:
                    _, doc = os.path.split(root)
                    view = parts.group(1)
                    what = parts.group(2)
                    if documents[doc].get(view) == None:
                        documents[doc][view] = {}
                    fh = open(os.path.join(root, name), 'r')
                    func = fh.read().strip()
                    fh.close()
                    if len(func)>0:
                        documents[doc][view][what]=func
        return documents
