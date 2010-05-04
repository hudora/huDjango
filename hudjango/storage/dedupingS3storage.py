#!/usr/bin/env python
# encoding: utf-8
"""
dedupingS3storage.py

Created by Maximillian Dornseif on 2010-05-04.
Copyright (c) 2010 HUDORA. All rights reserved.
"""

from storages.backends import s3boto
import hashlib

class dedupingS3(s3boto.S3BotoStorage):
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
        
        newname = hashlib.sha1(content).hexdigest()
        content.name = newname
        k = self.bucket.get_key(newname)
        if not k:
            k = self.bucket.new_key(newname)
        k.set_contents_from_file(content, headers=headers, policy=self.acl)
        return newname
    
    def delete(self, name):
        pass
