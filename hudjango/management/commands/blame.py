#!/usr/bin/env python

from django.core.management.base import BaseCommand
from django.contrib.sessions.models import Session
from django.contrib.auth.models import User
from django.utils.termcolors import colorize
import sys

class Command(BaseCommand):
    
    def handle(self, session_id, *args, **options):
        """Extract user id from session and display username."""

        try:
            session = Session.objects.get(pk=session_id)
        except Session.DoesNotExist:
            sys.stderr.write("Hey, I know who it is, it's %s!\n" % colorize('YOU', fg='red'))
            return
        try:
            user_id = session.get_decoded()['_auth_user_id']
            user = User.objects.get(pk=user_id)
            sys.stderr.write("Session is bound to user %s (%s)\n" % (colorize(user.get_full_name(), fg='green'), colorize(user.email, fg='green')))
        except KeyError:
            sys.stderr.write('No user id in session data\n')
        except User.DoesNotExist:
            sys.stderr.write('User from session data does not exist\n')
