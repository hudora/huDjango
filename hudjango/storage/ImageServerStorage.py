"""
This is a Custom Storage System for Django with CouchDB backend.
Created by Christian Klein.
(c) Copyright 2009 HUDORA GmbH. All Rights Reserved.
"""

from hudjango.storage.CouchDBStorage import CouchDBStorage
import huimages


class ImageServerStorage(CouchDBStorage):
    """
    ImageServerStorage - a Django Storage class for the huDjango ImageServer.
    """
    
    def __init__(self, **kwargs):
        self.typ = kwargs.get('type', None)
        
    def _put_file(self, name, content):
        if self.typ:
            return huimages.save_image(content, filename=name, typ=self.typ)
        return huimages.save_image(content, filename=name)
    
    def exists(self, name):
        try:
            huimages.get_size(name)
            return True
        except:
            return False
    
    def size(self, name):
        return huimages.get_size(name)
    
    def url(self, name):
        return huimages.imageurl(name)
    
    def delete(self, name):
        # OR: ignore silently?
        raise NotImplementedError("ImageServerStorage is not intended to support delete()")
    
    # Storage.listdir()
