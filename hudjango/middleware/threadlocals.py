# based on http://code.djangoproject.com/wiki/CookBookThreadlocalsAndUser
# http://lukeplant.me.uk/blog.php?id=1107301634
# http://svn.zyons.python-hosting.com/trunk/zilbo/common/utils/middleware/threadlocals.py
# slightly modidies by Maximillian Dornseif, September 2006

"""Hand request data down to non-request related functions.

Usually with request related information like remote IP address or logged  in user you are unable to access
this information in non-request related modules of the django stack, e.g. in models.
Handing down this information is somewhat tricky since we have to keep multi-threaded webservers in mind.

With this middleware you can use things like UpdatedByField and CreatedByIPField.
"""

# threadlocals middleware
try:
    from threading import local
except ImportError:
    from django.utils._threading_local import local

_thread_locals = local()


def set_current_user(user):
    """Stores the logged in user serviced by this thread"""
    _thread_locals.user = user


def get_current_user():
    """query the information stored by ThreadLocals."""
    return getattr(_thread_locals, 'user', None)


def set_remote_ip(ipaddr):
    """Stores the remote IP address serviced by this thread"""
    _thread_locals.remote_ip = ipaddr


def get_remote_ip():
    """query the information stored by ThreadLocals."""
    return getattr(_thread_locals, 'remote_ip', None)


class ThreadLocals(object):
    """Middleware that gets various objects from the
    request object and saves them in thread local storage."""

    def process_request(self, request):
        """Store certain data at every request."""
        set_current_user(getattr(request, 'user', None))
        set_remote_ip(request.META.get('REMOTE_ADDR', None))
