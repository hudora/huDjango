#!/usr/bin/env python
# encoding: utf-8
"""
dedupingS3storage.py

Created by Maximillian Dornseif on 2010-05-04.
Copyright (c) 2010 HUDORA. All rights reserved.
"""

from boto.s3.key import Key
from storages.backends import s3boto
import hashlib
import mimetypes
import os

def _compute_hash(fp):
    BufferSize = 4096*100
    m = hashlib.sha224()
    fp.seek(0)
    s = fp.read(BufferSize)
    while s:
        m.update(s)
        s = fp.read(BufferSize)
    fp.seek(0)
    return m.digest().encode('base64').replace('/', 'H').replace('+', 'D').strip('\n=')
    

class DedupingS3storage(s3boto.S3BotoStorage):
    """Based on S3BotoStorage this ensures that similar files are only saved once.
    
    Does NOT support deletion of files."""
    
    def _save(self, name, content):
        name = self._clean_name(name)
        headers = self.headers
        content_type = mimetypes.guess_type(name)[0] or "application/x-octet-stream"
        
        if self.gzip and content_type in self.gzip_content_types:
            content = self._compress_content(content)
            headers.update({'Content-Encoding': 'gzip'})
        
        headers.update({
            'Content-Type': content_type,
            'Content-Length' : len(content),
        })
        
        newname = _compute_hash(content)
        newname = newname + mimetypes.guess_extension(content_type)
        content.name = newname
        k = self.bucket.get_key(newname)
        if not k:
            k = self.bucket.new_key(newname)
            k.set_metadata('original_filename', name)
        k.set_contents_from_file(content, headers=headers, policy=self.acl)
        return newname

    def delete(self, name):
        pass

    def url(self, name):
        s3url = super(DedupingS3storage, self).url(name)
        if self.acl == 'public-read':
            s3url = s3url.split('?')[0]
        return s3url
