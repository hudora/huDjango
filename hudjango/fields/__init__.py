"""Extended fieldtypes for use with django.

defaulting        - set default values
scalingimagefield - ImageField variant  wich scales images on the fly.
"""

from hudjango.fields.defaulting import *
from hudjango.fields.scalingimagefield import *
from django.db.models import ManyToManyField


class RelaxedManyToManyField(ManyToManyField):
    """"This is a many to many field which can handle non integer primary keys for the relation."""
    
    def isValidIDList(self, field_data, all_data):
        "Validates that the value is a valid list of foreign keys"
        mod = self.rel.to
        pks = field_data.split(',')
        objects = mod._default_manager.in_bulk(pks)
        if len(objects) != len(pks):
            badkeys = [k for k in pks if k not in objects]
            raise validators.ValidationError, "Please enter valid %(self)s IDs." % {'self': self.verbose_name}
