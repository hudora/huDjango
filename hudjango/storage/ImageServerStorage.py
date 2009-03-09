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
import huimages
from PIL import Image


class ImageServerStorage(CouchDBStorage):
    """
    ImageServerStorage - a Django Storage class for the huDjango ImageServer.
    """
    
    def __init__(self, **kwargs):
        pass
        
    def _put_file(self, name, content):
        return huimages.save_image(content, filename=name, typ='product_image')
    
    def get_document(self, name):
        raise NotImplementedError
    
    def delete(self, name):
        raise IOError("ImageServerStorage is not intended to support delete()")
