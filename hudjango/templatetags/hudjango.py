#!/usr/bin/env python
# encoding: utf-8
"""
Created by Maximillian Dornseif on 2006-08-22.
Copyright (c) 2006-2008 HUDORA GmbH. Consider it BSD licensed.
"""

from django import template
from django.template import resolve_variable

register = template.Library()


def format_address(obj):
    """Formats the address in a Lieferung/Lieferschein/Kunde as nice XHTML.
    
    The obj must follow the address-protocol outlined at
    http://cybernetics.hudora.biz/projects/wiki/AddressProtocol
    
    The generated XHTML follows hCard described at http://microformats.org/wiki/hcard
    """
    
    ret = []
    kdnstr = '<span class="org name1">%s</span>' % obj.name1
    if hasattr(obj, 'kundennummer') and obj.kundennummer:
        kdnstr += ' (<span class="customerid">%s</span>)' % obj.kundennummer
    ret.append(kdnstr)
    for dataname in ['name2', 'name3']:
        data = ''
        if hasattr(obj, dataname):
            data = getattr(obj, dataname)
        if data:
            ret.append('<span class="%s">%s</span>' % (dataname, data))
    if hasattr(obj, 'iln') and obj.iln:
        kdnstr += 'ILN <span class="iln">%s</span>' % obj.iln
    
    ret.append('<span class="adr">')
    for dataname in ['adresse', 'address', 'street', 'strasse']:
        data = ''
        if hasattr(obj, dataname):
            data = getattr(obj, dataname)
        if data:
            ret.append('<span class="%s">%s</span>' % (dataname, data))
    if hasattr(obj, 'plz'):
        ortstr = ('<span class="zip postal-code">%s</span>'
                  ' <span class="city locality">%s</span>' % (obj.plz, obj.ort))
    else:
        ortstr = ('<span class="zip postal-code">%s</span>'
                  ' <span class="city locality">%s</span>' % (obj.postleitzahl, obj.ort))
    land = 'DE'
    if hasattr(obj, 'land'):
        land = obj.land
    else:
        land = obj.laenderkennzeichen
    if land != 'DE':
        ortstr = ('<span class="country-name land">%s</span>-' % land) + ortstr
    ret.append(ortstr)
    ret.append('</span">')
    
    # the whole thing is enclesed in a vcard class tag
    return '<div class="address vcard">%s</div>' % '<br/>'.join(ret)
register.filter(format_address)


def html_euro(value):
    """
    Formats a value with two decimal digits and adds an Euro sign in HTML entity notation.
    
    Example::
    
        {% 1.2345|html_euro %} results in 1.23&nbsp;&euro;
    """
    
    try:
        value = float(value)
    except ValueError:
        return value
    except TypeError:
        return value
    return "%.2f&nbsp;&euro;" % (value)
register.filter(html_euro)


def html_cent(value):
    """
    Formats a value with up to 5 decimal digits and andds an cent sign in HTML entity notation.
    
    Example::
    
        {% 0.00012345|html_cent %} results in 0.00012&nbsp;&cent;
    """
    
    try:
        value = float(value)
    except ValueError:
        return value
    except TypeError:
        return value
    return "%.5f&nbsp;&cent;" % (value)
register.filter(html_cent)


def g2kg(value):
    """
    Convert Gramms to kg by dividing by 1000.
    
    Example::
    
        {% 1000|g2kg %} results in 1
    """
    
    try:
        value = int(value)
    except ValueError:
        return value
    except TypeError:
        return value
    return "%d" % int(value/1000)
register.filter(g2kg)


class LinkObject(template.Node):
    """Helper class for do_link_object()."""
    
    def __init__(self, obj):
        super(LinkObject, self).__init__(obj)
        self.obj = obj
    
    def render(self, context):
        """Called when the page is actually rendered."""
        obj = resolve_variable(self.obj, context)
        if hasattr(obj, 'get_absolute_url'):
            return '<a href="%s">%s</a>' % (obj.get_absolute_url(), unicode(obj))
        return unicode(obj)
    

def do_link_object(dummy, token):
    """
    Create a Link to a Database Object.
    
    This uses an object's get_absolute_url() and __unicode__() methods to generate a link tag-pair to this
    object by basically transforming 
    
    Example::
    
        {% link_object %} to:
        <a href="obj.get_absolute_url()">str(obj)</a>
    
    If the object doesn't have a get_absolute_url() we fall back to just returning the string representation
    of the object.
    """
    try:
        # split_contents() knows not to split quoted strings.
        dummy, obj = token.contents.split()
    except ValueError:
        raise template.TemplateSyntaxError, "%r tag requires a single argument" % token.contents[0]
    return LinkObject(obj)
register.tag('link_object', do_link_object)
