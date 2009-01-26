from django.core.files.storage import Storage
from django.conf import settings
from django.core.files import File

from cStringIO import StringIO
import couchdb.client

from urlparse import urljoin
from urllib import quote_plus
from os.path import join


DEFAULT_SERVER = "http://boingball.local.hudora.biz:5984"


class CouchDBFile(File):
    def __init__(self, name, storage, mode):
        self._name = name
        self._storage = storage
        self._mode = mode
        self._is_dirty = False

        try:
            self._doc = self._storage.get_document(name)
            attachment = self._storage.db.get_attachment(self._doc, filename='content')
            self.file = StringIO(attachment)
        except couchdb.client.ResourceNotFound:
            if 'r' in self._mode:
                raise ValueError("The file cannot be reopened.")
            else:
                self.file = StringIO()
                self._is_dirty = True

    @property
    def size(self):
        return self._doc['size']

    def write(self, content):
        if 'w' not in self._mode:
            raise AttributeError("File was opened for read-only access.")
        self.file = StringIO(content)
        self._is_dirty = True

    def close(self):
        if self._is_dirty:
            self._storage._put_file(self._name, self.file.getvalue())
        self.file.close()


class CouchDBStorage(Storage):
    """
    CouchDBStorage - a Django Storage class for CouchDB.

    The CouchDBStorage can be configured in settings.py, e.g.:
    COUCHDB_STORAGE_OPTIONS = {'server': "http://boingball.local.hudora.biz:5984", 'database': 'produktpass_images'}

    Alternatively, the configuration can be passed as a parameter 'option' as a dictionary.
    """
    def __init__(self, option=None):
        config = settings.COUCHDB_STORAGE_OPTIONS
        if option:
            config.update(option)
        self.base_url = config.get('server', DEFAULT_SERVER)
        server = couchdb.client.Server(self.base_url)
        self.db = server[config.get('database')]

    def _put_file(self, name, content):
        self.db[name] = {'size': len(content)}
        self.db.put_attachment(self.db[name], content, filename='content')

    def get_document(self, name):
        return self.db.get(name)

    def _open(self, name, mode='rb'):
        couchdb_file = CouchDBFile(name, self, mode=mode)
        return couchdb_file

    def _save(self, name, content):
        content.open()
        if hasattr(content, 'chunks'):
            content_str = ''.join(chunk for chunk in content.chunks())
        else:
            content_str = content.read()
        self._put_file(name, content_str)
        return name

    def exists(self, name):
        return name in self.db

    def size(self, name):
        doc = self.get_document(name)
        if doc:
            return doc['size']
        return 0

    def url(self, name):
        return urljoin(self.base_url, join(quote_plus(self.db.name), quote_plus(name), 'content'))

    def delete(self, name):
        try:
            del self.db[name]
        except couchdb.client.ResourceNotFound:
            raise IOError("File not found: %s" % name)

    #def listdir(self, name):
    # _all_docs?
    #    pass
