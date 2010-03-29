#!/usr/bin/env python
# encoding: utf-8
"""
decorators.py

Created by Christian Klein on 2010-03-26.
Copyright (c) 2007 HUDORA GmbH. All rights reserved.
"""

from functools import wraps
from django.http import HttpResponse
import simplejson as json


# The ajax_request decorator was taken from django-annoying
# see http://pypi.python.org/pypi/django-annoying/0.7.4

class JsonResponse(HttpResponse):
    """
    HttpResponse descendant, which return response with ``application/json`` mimetype.
    """
    def __init__(self, data):
        super(JsonResponse, self).__init__(content=json.dumps(data), mimetype='application/json')


def ajax_request(func):
    """
    If view returned serializable dict, returns JsonResponse with this dict as content.

    example:

        @ajax_request
        def my_view(request):
            news = News.objects.all()
            news_titles = [entry.title for entry in news]
            return {'news_titles': news_titles}
    """
    @wraps(func)
    def wrapper(request, *args, **kwargs):
        response = func(request, *args, **kwargs)
        if isinstance(response, dict):
            return JsonResponse(response)
        else:
            return response
    return wrapper
