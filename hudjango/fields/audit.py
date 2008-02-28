# encoding: utf-8

"""Field types for Django which save audit-related information.

This needs the threadlocals middleware.

Created September 2006 by Maximillian Dornseif. Consider it BSD licensed."""

from django.db import models
from django.dispatch import dispatcher
from django.db.models import signals
from django.contrib.auth.models import User

from hudjango.middleware import threadlocals

class UpdatedByField(models.ForeignKey):
    """Stores the currently logged in user on every save."""
    def __init__(self, *args, **kwargs):
        kwargs['editable'] = False
        super(UpdatedByField, self).__init__(User, *args, **kwargs)
    
    def _set_user(self, instance=None):
        """Will be called by pre_save to set the current user."""
        if threadlocals.get_current_user():
            setattr(instance, self.attname, threadlocals.get_current_user().id)
    
    def contribute_to_class(self, cls, name):
        """Adds a pre_save signal handler to ensure _set_user() is called before beeing saved."""
        super(UpdatedByField, self).contribute_to_class(cls, name)
        dispatcher.connect(self._set_user, signals.pre_save, sender=cls)
    
    def get_internal_type(self):
        """Returns the 'real' tye used for the  database mapper."""
        return 'ForeignKey'
    

class CreatedByField(models.ForeignKey):
    """Stores the currently logged in user on creation."""
    def __init__(self, *args, **kwargs):
        if not 'editable' in kwargs:
            kwargs['editable'] = False
        super(CreatedByField, self).__init__(User, *args, **kwargs)
    
    def _set_user(self, instance=None):
        """Will be called by pre_save to set the current user."""
        if not instance.id:
            # This is a new object, set the owner 
            if threadlocals.get_current_user():
                setattr(instance, self.attname, threadlocals.get_current_user().id)
    
    def contribute_to_class(self, cls, name):
        """Adds a pre_save signal handler to ensure _set_user() is called before beeing saved."""
        super(CreatedByField, self).contribute_to_class(cls, name)
        dispatcher.connect(self._set_user, signals.pre_save, sender=cls)
    
    def get_internal_type(self):
        """Returns the 'real' tye used for the  database mapper."""
        return 'ForeignKey'
    

class UpdatedByIPField(models.IPAddressField):
    """Stores the remote IP Address on every save."""
    def __init__(self, *args, **kwargs):
        kwargs['editable'] = False
        super(UpdatedByIPField, self).__init__(User, *args, **kwargs)
    
    def _set_ip(self, instance=None):
        """Will be called by pre_save to set the current remote ip."""
        setattr(instance, self.attname, threadlocals.get_remote_ip())
    
    def contribute_to_class(self, cls, name):
        """Adds a pre_save signal handler to ensure _set_ip() is called before beeing saved."""
        super(UpdatedByIPField, self).contribute_to_class(cls, name)
        dispatcher.connect(self._set_ip, signals.pre_save, sender=cls)
    
    def get_internal_type(self):
        """Returns the 'real' tye used for the  database mapper."""
        return 'IPAddressField'
    

class CreatedByIPField(models.IPAddressField):
    """Stores the remote IP Address upon creation."""
    def __init__(self, *args, **kwargs):
        if not 'editable' in kwargs:
            kwargs['editable'] = False
        super(CreatedByIPField, self).__init__(User, *args, **kwargs)
    
    def _set_ip(self, instance=None):
        """Will be called by pre_save to set the current remote ip."""
        if not instance.id:
            # This is a new object, set the ip
            setattr(instance, self.attname, threadlocals.get_remote_ip())
    
    def contribute_to_class(self, cls, name):
        """Adds a pre_save signal handler to ensure _set_ip() is called before beeing saved."""
        super(CreatedByIPField, self).contribute_to_class(cls, name)
        dispatcher.connect(self._set_ip, signals.pre_save, sender=cls)
    
    def get_internal_type(self):
        """Returns the 'real' tye used for the  database mapper."""
        return 'IPAddressField'
    
