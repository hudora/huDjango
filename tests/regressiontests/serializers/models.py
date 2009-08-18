#!/usr/bin/env python
# encoding: utf-8
"""
regressiontests/serializers/models.py

Created by Maximillian Dornseif on 2009-08-17.
Copyright (c) 2009 HUDORA. All rights reserved.
"""

from django.db import models

class Place(models.Model):
    name = models.CharField(max_length=50)
    address = models.CharField(max_length=80)
    last_visit = models.DateTimeField()
    
    def __unicode__(self):
        return u"%s the place" % self.name
    
    def get_absolute_url(self):
        return 'http://testserver/place/%d/' % self.id
