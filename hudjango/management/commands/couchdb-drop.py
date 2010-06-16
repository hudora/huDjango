# encoding: utf-8

import couchdb
from hudjango.management.couchdb.support import CouchDBBaseCommand
from django.core.management.base import CommandError


class Command(CouchDBBaseCommand):
    help = """ Drop an existing couchdb database. """

    def handle(self, *args, **options):
        # get the name of the database to create
        if len(args) != 1:
            raise CommandError("You need to specify exactly one argument as database name")
        database = args[0]

        # drop a possibly existing database if the user wants us to.
        couch = self._server(options)
        try:
            couch.delete(database)
            print "database '%s' deleted succesfully" % database
        except couchdb.client.ResourceNotFound:
            print "unable to delete deleting database '%s'!" % database
