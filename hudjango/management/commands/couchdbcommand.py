# encoding: utf-8

from optparse import make_option
from django.core.management.base import BaseCommand
from uuid import uuid4
import couchdb
import re
import os
import json

import couchdb.client


class CouchDBCommand(BaseCommand):
    
    option_list = BaseCommand.option_list + (
        make_option('--server', '-s', default='http://localhost:5984/', help='couchdb server to use [default: %default]'),
        #make_option('--database', '-d', help='couchdb database to use'),
    )

    def _is_json_filename(self, filename):
        return os.path.splitext(filename)[-1] == ".json"

    def _server(self, servername):
        server = couchdb.client.Server(servername)
        return server

    def _db(self, options):
        db = self._server(options['server'])[options['database']]
        return db
    
    def _documents_path(self, options):
        path = os.path.join(options['path'], 'documents')
        return path

    def load_json_document(self, filepath):
        # zuerst laden wir das original Dokument
        try: 
            doc = json.load(open(filepath))
        except Exception:
            raise Exception("unable to parse json document '%s'!" % filepath)

        # wenn wir die ID geaendert haben speichern wir das Dokument noch
        if not '_id' in doc:
            doc_id = uuid4().hex
            fh = open(filepath, 'w')
            json.dump(doc, fh, indent=4, sort_keys=True)
            fh.close()
        
        # und jetzt das Document mit seiner ID zurueckliefern
        return doc['_id'], doc
