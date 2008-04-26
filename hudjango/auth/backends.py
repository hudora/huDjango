#!/usr/bin/env python
# encoding: utf-8
"""
backends.py - extended authentication login for django

Currently this module provides two authentication backends.

EmailBackend    - allows login using the E-Mail adress instead of the password.
ZimbraBackend   - allows authentication against a Zimbra-LDAP server with E-Mail address and Zimbra password.

Usage:

If you have installed huDjango you can edit the settings.py of your Django
Project to use the new authentication Backend. Add

AUTHENTICATION_BACKENDS = (
    'hudjango.auth.backends.EmailBackend', 
    'django.contrib.auth.backends.ModelBackend',
)

Created by Maximillian Dornseif on 2008-02-28.
Copyright (c) 2008 HUDORA. All rights reserved.
"""

import ldap
from django.conf import settings 
from django.contrib.auth.models import User
import django.contrib.auth.backends


class EmailBackend(django.contrib.auth.backends.ModelBackend):
    """
    Authenticate against django.contrib.auth.models.User the same way Django
    does by default except that the users can use their E-Mail
    address instead of the unsername to authenticate. This obviously
    leads to an awful lot of trouble if the E-Mail adresses in your 
    User Database are not unique.
    """

    def authenticate(self, username=None, password=None):
        """Authenticate a user with password."""
        
        # our auth strategy
        try:
            # 1. see if we find a user object with that username
            user = User.objects.get(username=username)
            if user.check_password(password):
                return user
        except User.DoesNotExist:
            # 2. see if we find a user object with that email adress
            users = User.objects.filter(email=username)
            if len(users) == 1 and users[0].check_password(password):
                return users[0]
        return None
    

class ZimbraBackend(django.contrib.auth.backends.ModelBackend):
    """
    Authenticate against a Zimbra Server via LDAP.
    
    Users have to use their full E-Mail adress and Zimbra Passwort to log in.
    This obviously leads to an awful lot of trouble if the E-Mail adresses in your 
    User Database are not unique.
    
    The Backend creates a new entry in the Django User Database if authentication
    against Zimbra is successfull but no matching E-Mail in Django adress is found.
    the new user gets the attribute is_staff = True.
    
    You can set your LDAP Servername in settuings using the variable LDAP_SERVER_NAME. E.g.:
    
    LDAP_SERVER_NAME = 'mail.local.hudora.biz'
    
    The code assumes the LDAP server allows "annonymous bind" (which is the default with Zimbra).
    """

    # this code is based in Django Ticket 2507 - http://code.djangoproject.com/attachment/ticket/2507
    # and code from Christian N Clein

    def authenticate(self, username=None, password=None):
        """Authenticate a user with password.
        
        Might also create the user in the Django User DB.
        """
        
        servername = 'mail.local.hudora.biz'
        if hasattr(settings, 'LDAP_SERVER_NAME'):
            servername = settings.LDAP_SERVER_NAME
        lconn = ldap.open(servername)
        lconn.protocol_version = ldap.VERSION3
        result_id = lconn.search('', ldap.SCOPE_SUBTREE, 'mail=%s' % (username, ),
                             ['uid', 'displayName', 'givenname', 'sn', 'mail', 'userPassword'])
        dummy, result_data = lconn.result(result_id, 0)
        
        # If the user does not exist in LDAP, Fail.
        if (len(result_data) != 1):
            lconn.unbind_s()
            return None
        uid, result_dict = result_data[0]
        
        # Attempt to bind to the user's DN (verify password)
        try:
            lconn.simple_bind_s(uid, password)
        except ldap.INVALID_CREDENTIALS: # Failed user/pass 
            # password wrong, exit
            return None 
        finally:
            lconn.unbind_s() 
        
        # get user DB from Django
        users = User.objects.filter(email=username)
        if len(users) == 1:
            # update django password
            users[0].set_password(password)
            users[0].save()
            return users[0]
        elif len(users) == 0:
            # generate user from LDAP in Django
            user = User()
            user.username = result_dict.get('uid')[0]
            user.first_name = result_dict.get('givenName')[0]
            user.last_name = result_dict.get('sn')[0]
            user.email = result_dict.get('mail')[0]
            user.is_staff = True
            user.is_active = True
            user.set_password(password)
            user.save()
            return user
        return None
