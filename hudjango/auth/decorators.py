#!/usr/bin/env python
# encoding: utf-8
"""
decorators.py - authentication related decorators

Created by Maximillian Dornseif on 2009-03-15.
Copyright (c) 2009 HUDORA. All rights reserved.
"""

import doctest
import sys
import django.contrib.auth
from functools import wraps, update_wrapper

from django.contrib.auth import authenticate, login
from django.http import HttpResponse


def get_credentials(authheader):
    r"""Extract HTTP-Basic Auth Credentials and return username, password).
    
    >>> get_credentials('basic dGVzdHVzZXI6dGVzdHBhc3N3b3Jk\n')
    ('testuser', 'testpassword')
    
    """
    
    if not authheader:
        return None, None
    
    authmeth, auth = authheader.split(' ', 1)
    if authmeth.lower() != 'basic':
        # return HttpResponse('unknown authentication method', status=406)
        return None, None
    
    auth = auth.strip().decode('base64')
    username, password = auth.split(':', 1)
    return username, password
    

def require_login(func):
    """This decorator logs in a user via HTTP-Auth.
    
    It dos NOT require HTTP Auth is the user already has an active session.
    If the users send via HTTP-Auth differs from the user in the active session, the Session is
    dumped and login with the cedentials provided via HTTP-Auth is retried.
    """
    
    @wraps(func)
    def _decorator(request, *args, **kwargs):
        # no docstring since docstring will be overwritten by the decorated function
        username, password = get_credentials(request.META.get('HTTP_AUTHORIZATION'))
        
        if request.user.is_authenticated():
            if username and username not in [request.user.username, request.user.email]:
                # username given in HTTP-Auth differs from username in session. This should never happen.
                # logout and force reauthentication.
                django.contrib.auth.logout(request)
                response = HttpResponse('Authentication required', status=401)
                response['WWW-Authenticate'] = 'Basic realm="Internal"'
                return response
            else:
                if not request.user.is_active:
                    return HttpResponse('disabled account', status=403)
                # user already is logged in, just proceed to the wrapped function
                return func(request, *args, **kwargs)
        
        # user is not logged in and didn't provide authentication credentials - request authentication
        if 'HTTP_AUTHORIZATION' not in request.META:
            response = HttpResponse('Authentication required', status=401)
            response['WWW-Authenticate'] = 'Basic realm="Internal"'
            return response
            
        if not username:
            return HttpResponse('unknown authentication method', status=406)
        
        # Ask Django to do authentication for us.
        user = authenticate(username=username, password=password)
        
        if user:
            if not user.is_active:
                return HttpResponse('disabled account', status=403)
            else:
                login(request, user)
                return func(request, *args, **kwargs)
        else:
            # Django didn't find anything, ask for authentication again.
            response = HttpResponse('invalid login', status=401)
            response['WWW-Authenticate'] = 'Basic realm="Internal"'
            return response
    
    return _decorator


def deny_unless_user_passes_test(test_func):
    """Decorator that thecks if a user passes a test and if not renders a failure message.
    
    The decorator assumes the user is already authenticated. You might want to use it in conjunction
    with require_login.
    
    Similar to django.contrib.auth.decorators.user_passes_test but without redirection.
    """
    
    def wrap(func):
        print "WWW", func, test_func
        # @wraps(func)
        def _decorator(request, *args, **kwargs):
            print "deco!", test_func, request.user, test_func(request.user)
            if not test_func(request.user):
                return HttpResponse('Access denied / Zugriff verweigert (%s:%s)' % (request.user.id,
                            request.user.username), status=403)
            return func(request, *args, **kwargs)
        return _decorator
    return wrap

if __name__ == '__main__':
    failure_count, test_count = doctest.testmod()
    sys.exit(failure_count)
