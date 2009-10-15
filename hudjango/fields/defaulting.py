#!/usr/bin/env python
# encoding: utf-8

"""
defaulting.py

Django fields with more elaborate default values.

Created by Maximillian Dornseif on 2006-11-12. Consider it BSD licensed.
"""

from django.db import models
from django.db.models import signals


class DefaultingCharField(models.CharField):
    """Results in a dynamic default value - basically if no value is given the field is filled from an 
       other field during saving.
    """
    # we might  be able to get the same effect with a callable default but I dont know how to ensure 
    # that the field  referenced is already set when the callable is executed.
    def __init__(self, default_from_field=None, *args, **kwargs):
        self.default_from_field = default_from_field
        super(DefaultingCharField, self).__init__(*args, **kwargs)
    
    def _set_default(self, instance=None, **kwargs):
        """Will be called by pre_save to set a default value if the attribute is not set."""
        if not self.default_from_field:
            return
        if not getattr(instance, self.attname):
            if len(getattr(instance, self.default_from_field)) <= self.max_length:
                setattr(instance, self.attname, instance.name)
    
    def contribute_to_class(self, cls, name):
        """Adds a pre_save signal handler to ensure we can set the defaults before beeing saved."""
        super(DefaultingCharField, self).contribute_to_class(cls, name)
        signals.pre_save.connect(self._set_default, sender=cls)
    
    def get_internal_type(self):
        return 'CharField'
    
#class untitled:
#    def __init__(self):
#        pass

#class untitledTests(unittest.TestCase):
#    def setUp(self):
#        pass

#if __name__ == '__main__':
#    unittest.main()
