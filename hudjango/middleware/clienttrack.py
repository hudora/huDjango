#!/usr/bin/env python
# encoding: utf-8
"""
middleware.py tracks clients by setting a persistent unique coockie.

You can access it via request.clienttrack_uid in your views.
There is also request.clienttrack_first_visit and request.clienttrack_last_visit
available to your views. See ClientTrackMiddleware for details.

Always keep in mind that Coockies can easily be faked.

This has no dependencies on django.contrib.auth and django.contrib.sessions.

Created by Maximillian Dornseif on 2009-02-07.
Copyright (c) 2009 HUDORA. All rights reserved.
"""

import base64
import hashlib
import random
import time
from django.utils.http import cookie_date


def _gen_uid():
    return base64.b32encode(hashlib.md5("%f-%f" % (random.random(), time.time())).digest()).rstrip('=')
    

class ClientTrackMiddleware(object):
    """The ClientTrackMiddleware tracks Clients (Browsers) by setting a unique cookie.
    
    Assuming cookies work as advertised you can access the following variables in your view functions:
    
    * request.clienttrack_uid (always set) - unique ID we assigned to the client.
      Keep in mind that this is trival to fake.
    * request.clienttrack_first_visit - time.time() value at the very first time the client accessed our
      server or None for first time visitors.
    * request.clienttrack_last_visit - time.time() value at the very time the client last accessed our
      server or None.
    """
    
    def process_request(self, request):
        if '_hda' in request.COOKIES:
            parts = request.COOKIES.get('_hda').split(',')
            request.clienttrack_first_visit, request.clienttrack_uid \
                = parts[:2]
            if len(parts) > 3:
                request.clienttrack_last_visit = parts[2]
            else:
                request.clienttrack_last_visit = None
        else:
            request.clienttrack_uid = _gen_uid()
            request.clienttrack_last_visit = request.clienttrack_first_visit = None
    
    def process_response(self, request, response):
        # warning: when process_response() is called it might be, that process_request()
        # was NOT called before on the process object
        if (not getattr(request, 'clienttrack_prohibit', False)) or \
          not getattr(request, 'clienttrack_first_visit', None):
            # even if clienttrack_prohibit is True, we we set the cookie for first time visitors. 
            if not getattr(request, 'clienttrack_first_visit', None):
                request.clienttrack_first_visit = time.time()
            max_age = 3*365*24*60*60  # 3 years
            expires_time = time.time() + max_age
            expires = cookie_date(expires_time)
            response.set_cookie('_hda', "%s,%s,%f" % (request.clienttrack_first_visit,
                                                      getattr(request, 'clienttrack_uid', _gen_uid()),
                                                      time.time()),
                                max_age=max_age, expires=expires)
        return response
