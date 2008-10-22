# -*- coding: utf-8 -*-

"""Validators extending DJANGO.

See http://www.djangoproject.com/documentation/forms/#validators for more documentation on Django's
validators. Hopfully the validators below are all self explanatory."""

# Coded 2006 by Maximillian Dornseif for HUDORA GmbH
# You may use this under a "BSD License".

try: 
    #1.0
    from django.core.exceptions import ValidationError
except ImportError:
    #pre r8616
    from django.core.validators import ValidationError


class IsLessOrEqualThanOtherField(object):
    """Takes a field name and validates that the current field being validated has a value that is less
    than (or equal to) the other field's value. Comparisons are done using floats.
    
    This is a Variation of Django's IsLessThanOtherField."""

    def __init__(self, other_field_name, error_message = None):
        self.always_test = True
        self.other, self.error_message = other_field_name, error_message
        if not self.error_message:
            self.error_message = 'Dieses Feld darf nicht größer als Feld %r sein.' % self.other
    
    def __call__(self, field_data, all_data):
        if not field_data:
            return
        try:
            field_data = float(field_data)
        except Exception:
            try:
                field_data = int(field_data)
            except Exception:
                return
        try:
            other_data = float(all_data[self.other])
        except Exception:
            try:
                other_data = int(all_data[self.other])
            except Exception:
                return
        
        if field_data > other_data:
            raise ValidationError(self.error_message)
    

class IsLessOrEqualThan(object):
    """Validates that the current field is lower than the given value."""
    
    def __init__(self, maxvalue, error_message = None):
        self.always_test = True
        self.maxvalue, self.error_message = float(maxvalue), error_message
        if not self.error_message:
            self.error_message = 'Dieses Feld darf nicht größer als %r sein.' % self.maxvalue
    
    def __call__(self, field_data, dummy):
        if not field_data:
            return
        try:
            field_data = float(field_data)
        except Exception:
            try:
                field_data = int(field_data)
            except Exception:
                return
        
        if field_data > self.maxvalue:
            raise ValidationError(self.error_message)
