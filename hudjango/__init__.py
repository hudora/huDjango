"""This module collects several extensions to Django we found useful at HUDORA.
See http://www.djangoproject.com/ and https://cybernetics.hudora.biz/projects/wiki/huDjango

"""

import datetime
from django.contrib.admin.models import LogEntry
from django.contrib.auth.models import User
from django.contrib.contenttypes.models import ContentType
from django.utils.encoding import smart_unicode


class PrinterChooser(object):
    """PrinterChooser allows the user in a HTML form to choose a printer. It remembers the choice.
    PrinterChooser() must be initialized with
    
    * A Django Request Object
    * A list of possible printer names. The first name is the default choice.
    * An optional identifier if you want to use PrinterChooser() for different kinds of printers.
      We use 'a4', 'a4color' and 'label'.
    
    To use it your view must be structured like this:
    
        def myview(request):
            printer = PrinterChooser(request, ('DruckerErikBloodaxe', 'DruckerNapster'), 'label')
            ...
            print "Currently selected printer is %s" % printer.name
            response = render_to_response('huLOG/packstuecke_bearbeiten.html',
                                          printer.update_context({'lieferung': lieferung}),
                                          context_instance=RequestContext(request))
            populate_xheaders(request, response, Sendung, lieferung.id)
            return printer.update_response(response)
            
        
    In your template do:
    
        {% load hudjango %}
        ...
        <form ...>
        {% printer_choice %}
        ...
        </form>
        
    See http://static.23.nu/md/Pictures/ZZ5FB43EF0.png for an example.
    """

    def __init__(self, request, choices, name='default'):
        self.request = request
        self.choices = choices
        self.classname = name

    def update_response(self, response):
        """Updates an django Response Object to set the printer choice.

        Usually called in the last line of a Django view function:
            return printer.update_response(render_to_response(...))
        """

        printer_choice = self.request.POST.get('printer_choice', None)
        if printer_choice:
            max_age = 365*24*60*60  # one year
            expires = datetime.datetime.strftime(datetime.datetime.utcnow()
                        + datetime.timedelta(seconds=max_age), "%a, %d-%b-%Y %H:%M:%S GMT")
            response.set_cookie('printer_choice_%s' % self.classname, printer_choice,
            max_age=max_age, expires=expires)
            self.request.session['printer_choice'] = printer_choice
        return response

    def update_context(self, contextdict=None):
        """Update a Django template context (dict) in regard to the printer choices.

        Usually called in a Django view function as a parameter to render_to_response():
            response = render_to_response('foo.html', printer.update_context({'var1': 'val1', ...}))
        """

        if not contextdict:
            contextdict = {}
        contextdict.update({'printer_choice_list': self.choices,
                            'printer_choice': self.name})
        return contextdict

    @property
    def name(self):
        """Represents the currently choosen printer name."""

        printer_choice = self.request.POST.get('printer_choice')
        if not printer_choice:
            printer_choice = self.request.COOKIES.get('printer_choice_%s' % self.classname)
        if not printer_choice:
            self.request.session.get('printer_choice', self.choices[0])
        return printer_choice


def log_action(obj, action, user=None, message='', reprstr=None):
    """Adds a Django Admin Log entry.

    Arguments
     * obj: The object which is influenced by this action
     * action: one of the actions in django.contrib.admin.models; ADDITION, CHANGE, DELETION
     * user: the user which is responsible for this action. Defaults to user 'logger'
     * message: A short message containing information about the action
     * reprstr: a representation of the object

    """
    # from https://svn.python.org/conference/django/trunk/pycon/propmgr/changelog.py
    content_t = ContentType.objects.get_for_model(type(obj))
    if user is None:
        log_user = User.objects.get(username='logger')
        uid = log_user.id
    else:
        uid = user.id

    if reprstr == None:
        reprstr = smart_unicode(repr(obj))
    else:
        reprstr = smart_unicode(reprstr)
    LogEntry.objects.log_action(uid, content_t.id, obj.id, reprstr, action, message)
