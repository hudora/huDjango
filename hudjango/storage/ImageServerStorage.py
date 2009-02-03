"""
This is a Custom Storage System for Django with CouchDB backend.
Created by Christian Klein.
(c) Copyright 2009 HUDORA GmbH. All Rights Reserved. 
"""

from hudjango.storage.CouchDBStorage import CouchDBStorage
from cStringIO import StringIO
import hashlib
import base64
import os
from PIL import Image


class ImageServerStorage(CouchDBStorage):
    """
    ImageServerStorage - a Django Storage class for the huDjango ImageServer.
    """

    def _put_file(self, name, content):
        image = Image.open(StringIO(content))
        width, height = image.size
        doc_id = "%s01" % base64.b32encode(hashlib.md5(content).digest())
        self.db[doc_id] = {'name': name, 'size': len(content), 'height': height, 'width': width}
        self.db.put_attachment(self.db[doc_id], content, filename='content.%s' % os.path.splitext(name)[1])

    def delete(self, name):
        raise IOError("ImageServerStorage is not intended to support delete()")
