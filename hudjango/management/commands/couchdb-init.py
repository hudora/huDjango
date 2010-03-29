# encoding: utf-8

import couchdb
from optparse import make_option
from hudjango.management.commands.couchdbcommand import CouchDBCommand
from django.core.management.base import CommandError


class Command(CouchDBCommand):
    help = """Creates a new couchdb database."""
    option_list = CouchDBCommand.option_list + (
        make_option('--purge', '-p', action='store_true', help='Delete existing database [default: %default]'),
    )
    
    def handle(self, *args, **options):
        if len(args) != 1:
            raise CommandError("You need to specify exactly one argument as database name")
        database = args[0]
        server = couchdb.client.Server(options['server'])

        if options['purge']:
            try:
                server.delete(database)
            except couchdb.client.ResourceNotFound:
                pass
        
        try:
            server.create(database)
        except couchdb.client.PreconditionFailed, exception:
            raise CommandError("%s: %s" % (database, exception.message[1]))
        print "database '%s' created succesfully" % database
