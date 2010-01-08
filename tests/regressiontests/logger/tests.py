
# encoding: utf-8
"""
Created by Johan Otten on 2009-10-12.
Copyright (c) 2009 HUDORA. All rights reserved.
"""

from datetime import datetime

from django.test import TestCase
from django.contrib.admin.models import CHANGE, ADDITION
from django.contrib.auth.models import User

from hudjango import log_action
from regressiontests.serializers.models import Place


class TestLog(TestCase):
    """Test the logaction wrapper function."""

    def setUp(self):
        """Create a entry in the database."""
        self.place1 = Place.objects.create(name="Dempsey's", address="623 Vermont St",
                                      last_visit=datetime(2008, 7, 6, 5, 4, 3))
        self.place2 = Place.objects.create(name="Eich", address=u"An dür Eich 1",
                                      last_visit=datetime(2008, 7, 6, 5, 4, 3))

        self.user = User.objects.create_user('logger', 'lennon@example.com', 'logger')
        self.user2 = User.objects.create_user('logger2', 'lennon@example.com', 'logger2')


    def test_log_action(self):
        """Test the log_action function."""
        # test the most simplest form.
        log_action(self.place1, CHANGE)

        log_action(self.place2, ADDITION, self.user2)

        log_action(self.place2, ADDITION, self.user2, "this is a message")

        log_action(self.place2, ADDITION, self.user2, "this is a message", u"this is the repr")

