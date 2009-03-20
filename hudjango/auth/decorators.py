#!/usr/bin/env python
# encoding: utf-8
"""
decorators.py - authentication related decorators

Created by Maximillian Dornseif on 2009-03-15.
Copyright (c) 2009 HUDORA. All rights reserved.
"""

from functools import wraps
from django.contrib.auth import authenticate, login
from django.http import HttpResponse

def require_login(func):
    """This decorator logs in a user via HTTP-Auth."""
    @wraps(func)
    def _decorator(request, *args, **kwargs):
        if not request.META.has_key('HTTP_AUTHORIZATION'):
            response = HttpResponse('Authentication required', status=401)
            response['WWW-Authenticate'] = 'Basic realm="HUDORA Internal"'
            return response
            
        authmeth, auth = request.META['HTTP_AUTHORIZATION'].split(' ', 1)
        if authmeth.lower() != 'basic':
            return HttpResponse('unknown authentication method', status=406)

        auth = auth.strip().decode('base64')
        username, password = auth.split(':', 1)
        user = authenticate(username=username, password=password)
        if not user:
            response = HttpResponse('invalid login', status=401)
            response['WWW-Authenticate'] = 'Basic realm="HUDORA Internal"'
            return response
            
        if not user.is_active:
            return HttpResponse('disabled account', status=403)
            
        login(request, user)
        return func(request, *args, **kwargs)

    return _decorator
