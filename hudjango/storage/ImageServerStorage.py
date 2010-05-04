"""
This is a Custom Storage System for Django with CouchDB backend.
Created by Christian Klein.
(c) Copyright 2009 HUDORA GmbH. All Rights Reserved.
"""

from hudjango.storage.CouchDBStorage import CouchDBStorage
huimages = None  # lazy import, see ImageServerStorage.__init__()


class ImageServerStorage(CouchDBStorage):
    """ImageServerStorage - a Django Storage class for the huDjango ImageServer."""
    
    def __init__(self, **kwargs):
        global huimages
        if huimages is None:
            import huimages
        self.typ = kwargs.get('type', None)
        
    def _put_file(self, name, content):
        """Put file on the server."""
        if self.typ:
            return huimages.save_image(content, filename=name, typ=self.typ)
        return huimages.save_image(content, filename=name)
    
    def exists(self, name):
        """Check if an File/Image exists."""
        try:
            huimages.get_size(name)
            return True
        except:
            return False
    
    def size(self, name):
        """Return the dimensions (x, y) of an image."""
        return huimages.get_size(name)
    
    def url(self, name):
        """Return the URL where an Image can be accessed."""
        return huimages.imageurl(name)
    
    def delete(self, name):
        """Delete an Image - not implemented so far."""
        pass
        
    def listdir(self, path):
        """List a directory - not supported by this storage engine"""
        pass
