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
    m = hashlib.md5()
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
        extension =  mimetypes.guess_extension(content_type)
        if extension:
            newname = newname + extension
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

        # wir haben das Problem, das boto Links mit 'https' als Protocol rauswirft. Das 
        # kollidiert dann aber leider mit unseren Buckets, die dummerweise Punkte im 
        # Namen haben. In diesem Fall erkennt Jasper das Wildcard-Certificate von der S3-
        # Seite bei Amazon nicht mehr an, da Java der Meinung ist, das die URL 
        #    https://files.hudora.de.s3.amazonaws.com/DXsbvHxrkybbrwhjC4g4YA.gif
        # nicht durch das Wildcard-Certificate vom Amazon
        #    http://*.s3.amazonaws.com/
        # abgedeckt ist. @cklein hat eine schoene Loesung als Patch fuer S3Storage entwickelt,
        # bei der man Boto einfach so konfigurieren kann, das es http-Links generiert: 
        #    https://bitbucket.org/cklein/django-storages/changeset/c6b17f87443d
        # Der Patch wurde aber upstream nicht akzeptiert, sodass hier jetzt eine pragmatische
        # Loesung zu Einsatz kommt: Wenn der Bucket Punkte im Namen hat und der Links als 
        # https-Link generiert wurde wird einfach das https-Protokoll durch http ersetzt.
        if s3url.startswith('https:') and self.bucket.name.find('.') != -1:
            s3url = s3url.replace('https', 'http')
            
        return s3url
