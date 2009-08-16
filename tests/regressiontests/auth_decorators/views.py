#!/usr/bin/env python
# encoding: utf-8
"""
tests/auth_decorators/views.py

Created by Maximillian Dornseif on 2009-08-15.
Copyright (c) 2009 HUDORA. All rights reserved.
"""

from django.http import HttpResponse
from hudjango.auth.decorators import require_login


@require_login
def require_login_view(request):
    return HttpResponse('access!', status=200, mimetype='text/plain')
