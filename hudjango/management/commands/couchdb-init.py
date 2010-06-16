# encoding: utf-8

import couchdb
from optparse import make_option
from hudjango.management.couchdb.support import CouchDBBaseCommand
from django.core.management.base import CommandError


class Command(CouchDBBaseCommand):
    help = """ Creates a new couchdb database. """
    option_list = CouchDBBaseCommand.option_list + (
        make_option('--purge', action='store_true', help='Delete existing database [default: %default]'),
    )
    
    def handle(self, *args, **options):
        # get the name of the database to create
        if len(args) != 1:
            raise CommandError("You need to specify exactly one argument as database name")
        database = args[0]

        # drop a possibly existing database if the user wants us to.
        couch = self._server(options)
        if options['purge']:
            try:
                couch.delete(database)
            except couchdb.client.ResourceNotFound:
                pass
        
        # then create the new database
        try:
            couch.create(database)
        except couchdb.client.PreconditionFailed, exception:
            raise CommandError("%s: %s" % (database, str(exception)))
        print "database '%s' created succesfully" % database
