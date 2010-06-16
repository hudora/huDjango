import couchdb
import re
import os
import json

from hudjango.management.couchdb.support import CouchDBBaseCommand


class Command(CouchDBBaseCommand):
    help = """ Ensure that all documents are valid JSON-formatted files """

    def handle(self, *args, **options):
        errors_found = 0
        for root, dirs, files in os.walk(self._documents_path(options), topdown=True):
            for name in files:
                if self._is_json_filename(name):
                    filepath = os.path.join(root, name)
                    try: 
                        fh = open(filepath, 'r')
                        doc = json.load(fh)
                        fh.close()
                    except Exception as ex:
                        errors_found+=1
                        print "%s: %s" % (filepath,str(ex))

        if errors_found == 0:
            print "no JSON formatting errors found"
        else:
            print "found %d error(s)" % errors_found
