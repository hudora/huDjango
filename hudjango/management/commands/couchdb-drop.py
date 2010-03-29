# encoding: utf-8

import couchdb
from hudjango.management.commands.couchdbcommand import CouchDBCommand
from django.core.management.base import CommandError


class Command(CouchDBCommand):
    help = """Drop a couchdb database"""

    def handle(self, *args, **options):
        if len(args) != 1:
            raise CommandError("You need to specify exactly one argument as database name")
        database = args[0]
        server = couchdb.client.Server(options['server'])
        try:
            server.delete(database)
        except couchdb.client.ResourceNotFound:
            pass

        print "Database '%s' dropped succesfully" % database
