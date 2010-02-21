#!/usr/bin/env python
# encoding: utf-8
"""
Django Template Tags

Created by Maximillian Dornseif on 2006-08-22.
Copyright (c) 2006-2008 HUDORA GmbH. Consider it BSD licensed.
"""

import operator
import urllib
from django import template
from django.template import resolve_variable
from django.utils.html import conditional_escape
from django.utils.text import smart_split
from django.utils.safestring import mark_safe
huimages = None # lazy import, see ImageLink.__init__()


register = template.Library()


@register.filter
def format_location(value, dummy):
    """
    Formats a myPL location nicely.
    """
    
    # TODO: move to myPLfrontend - this is not of general interest.
    if len(value) == 6 and str(value).isdigit():
        return "%s-%s-%s" % (value[:2], value[2:4], value[4:])
    return value


@register.filter
def slashencode(value):
    """
    Like Django's urlencode but also encodes slashes.
    Example::
    
        {% 14600/WK|slashencode %} results in 14600%2FWK;
    """
    
    return urllib.quote(value, '')


@register.filter
def format_address(obj, autoescape=None):
    """Formats the address in a Lieferung/Lieferschein/Kunde as nice XHTML.

    The obj must follow the address-protocol outlined at
    http://cybernetics.hudora.biz/projects/wiki/AddressProtocol

    The generated XHTML follows hCard described at http://microformats.org/wiki/hcard
    """

    ret = []
    if autoescape:
        esc = conditional_escape
    else:
        esc = lambda x: x

    kdnstr = '<span class="org name1">%s</span>' % esc(obj.name1)
    if hasattr(obj, 'kundennr') and obj.kundennr:
        kdnstr += ' (<span class="customerid">%s</span>)' % esc(obj.kundennr)
    if hasattr(obj, 'kundennummer') and obj.kundennummer: # TODO: remove support for kundennummer (legacy)
        kdnstr += ' (<span class="customerid">%s</span>)' % esc(obj.kundennummer)
    ret.append(kdnstr)
    for dataname in ['name2', 'name3']:
        data = ''
        if hasattr(obj, dataname):
            data = getattr(obj, dataname)
        if data:
            ret.append('<span class="%s">%s</span>' % (dataname, esc(data)))
    if hasattr(obj, 'iln') and obj.iln:
        kdnstr += 'ILN <span class="iln">%s</span>' % esc(obj.iln)
    ret.append('<span class="adr">')
    for dataname in ['adresse', 'address', 'street', 'strasse']:
        data = ''
        if hasattr(obj, dataname):
            data = getattr(obj, dataname)
        if data:
            ret.append('<span class="%s">%s</span>' % (dataname, esc(data)))
    if hasattr(obj, 'plz'):
        ortstr = ('<span class="zip postal-code">%s</span>'
                  ' <span class="city locality">%s</span>' % (esc(obj.plz), esc(obj.ort)))
    else:
        ortstr = ('<span class="zip postal-code">%s</span>'
                  ' <span class="city locality">%s</span>' % (esc(obj.postleitzahl), esc(obj.ort)))
    land = 'DE'
    if hasattr(obj, 'land'):
        land = obj.land
    else:
        land = obj.laenderkennzeichen
    if land != 'DE':
        ortstr = ('<span class="country-name land">%s</span>-' % esc(land)) + ortstr
    ret.append(ortstr)
    ret.append('</span>')
    # the whole thing is enclesed in a vcard class tag
    return mark_safe('<div class="address vcard">%s</div>' % '<br/>'.join(ret))
format_address.needs_autoescape = True


def _get_attr(obj, key):
    """Get an object attribute or an dict key"""
    ret = getattr(obj, key, '')
    if (not ret) and hasattr(obj, 'get'):
        ret = obj.get(key, '')
    return ret


@register.filter
def format_addressproto(obj, autoescape=None):
    """Formats the address as nice XHTML. Includes telephone number and the like.
    
    The obj must follow the address-protocol outlined at
    http://github.com/hudora/huTools/blob/master/doc/standards/address_protocol.markdown
    
    The generated XHTML follows hCard described at http://microformats.org/wiki/hcard
    
    Works with objects:
    >>> class Dummy(object): pass
    >>> addr = Dummy()
    >>> addr.name1 = 'nameTEST'
    >>> format_addressproto(addr)
    '<div class="address vcard"><span class="org name1">nameTEST</span><br/><span class="adr"><span class="zip postal-code"></span> <span class="city locality"></span></span></div>'
    
    Works also with dicts:
    >>> format_addressproto({'name1': 'TESTname', 'ort': 'Rade', 'plz': '42477'})
    '<div class="address vcard"><span class="org name1">TESTname</span><br/><span class="adr"><span class="zip postal-code">42477</span> <span class="city locality">Rade</span></span></div>'
    """
    # it also supports some legacy variants of the address-protocol
    
    ret = []
    if autoescape:
        esc = conditional_escape
    else:
        esc = lambda x: x
    
    kdnstr = '<span class="org name1">%s</span>' % esc(_get_attr(obj, 'name1'))
    if _get_attr(obj, 'kundennr'):
        kdnstr += ' (<span class="customerid">%s</span>)' % esc(_get_attr(obj, 'kundennr'))
    elif _get_attr(obj, 'softmid'):
        kdnstr += ' (<span class="customerid">SC%s</span>)' % esc(_get_attr(obj, 'softmid'))
    elif _get_attr(obj, 'curmid'):
        kdnstr += ' (<span class="customerid">%s</span>)' % esc(_get_attr(obj, 'curmid'))
    ret.append(kdnstr)

    for dataname in ['name2', 'name3']:
        data = _get_attr(obj, dataname)
        if data:
            ret.append('<span class="%s">%s</span>' % (dataname, esc(data)))
    
    if _get_attr(obj, 'iln'):
        kdnstr += 'ILN <span class="iln">%s</span>' % esc(_get_attr(obj, 'iln'))
    
    addr = []
    for dataname in ['adresse', 'address', 'street', 'strasse']:
        data = _get_attr(obj, dataname)
        if data:
            addr.append('<span class="%s">%s</span>' % (dataname, esc(data)))
    if _get_attr(obj, 'plz'):
        ortstr = ('<span class="zip postal-code">%s</span>'
                  ' <span class="city locality">%s</span>' % (esc(_get_attr(obj, 'plz')),
                                                              esc(_get_attr(obj, 'ort'))))
    else:
        ortstr = ('<span class="zip postal-code">%s</span>'
                  ' <span class="city locality">%s</span>' % (esc(_get_attr(obj, 'postleitzahl')),
                                                              esc(_get_attr(obj, 'ort'))))
    land = _get_attr(obj, 'land')
    if not land:
        land = _get_attr(obj, 'laenderkennzeichen')
    if not land:
        land = 'DE'
    if land != 'DE':
        ortstr = ('<span class="country-name land">%s</span>-' % esc(land)) + ortstr
    addr.append(ortstr)
    ret.append('<span class="adr">%s</span>' % '<br/>'.join(addr))
    
    if _get_attr(obj, 'tel'):
        ret.append('<span class="tel"><span class="type">main</span>:<span class="value">%s</span></span>'
                   % esc(_get_attr(obj, 'tel')))
    if _get_attr(obj, 'mobile'):
        ret.append('<span class="tel"><span class="type">mobile</span>:<span class="value">%s</span></span>'
                   % esc(_get_attr(obj, 'mobile')))
    if _get_attr(obj, 'fax'):
        ret.append('<span class="tel"><span class="type">fax</span>:<span class="value">%s</span></span>'
                   % esc(_get_attr(obj, 'fax')))
    if _get_attr(obj, 'email'):
        ret.append('<span class="email">%s</span>' % esc(_get_attr(obj, 'email')))
    
    # the whole thing is enclesed in a vcard class tag
    return mark_safe('<div class="address vcard">%s</div>' % '<br/>'.join(ret))
format_addressproto.needs_autoescape = True


@register.filter
def deumlaut(value):
    """
    Converts Umlauts to ae, oe, etc.
    
    Example::
    
        {% Würstchen|deumlaut %} results in Wuerstchen
    """
    
    # TODO: use huTools.unicode.deUmlaut()
    value = value.replace('ß', 'ss').replace('ö', 'oe').replace('ä', 'ae').replace('ü', 'ue')
    return value.replace('Ö', 'Oe').replace('Ä', 'Ae').replace('Ü', 'ue')


@register.filter
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
    return mark_safe('%.2f&nbsp;&euro;' % (value))


@register.filter
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
    return mark_safe('%.5f&nbsp;&cent;' % (value))


@register.filter
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
    return mark_safe('%d' % int(value/1000))


def _cond_helper(func, arguments):
    """
    Helper function for the conditional filters.
    
    The arguments are converted to float numbers before
    the comparison function is applied.
    
    >>> _cond_helper(operator.gt, (0, 1))
    False
    
    >>> _cond_helper(operator.gt, (1, 0))
    True
    
    >>> _cond_helper(operator.lt, ("1", 2.3))
    True
    
    >>> _cond_helper(operator.le, ("abc", 0))
    False
    
    """
    try:
        numbers = [float(tmp) for tmp in arguments]
        return func(*numbers)
    except ValueError:
        return False
    

@register.filter(name='lt')
def lt_filter(value, arg):
    """Return if the float representation of value is less than the float representation of arg."""
    return _cond_helper(operator.lt, (value, arg))
    

@register.filter(name='le')
def le_filter(value, arg):
    """Return if the float representation of value is less than or equal to arg."""
    return _cond_helper(operator.le, (value, arg))
    

@register.filter(name='gt')
def gt_filter(value, arg):
    """Return if the float representation of value is greater than the float representation of arg."""
    return _cond_helper(operator.gt, (value, arg))
    

@register.filter(name='ge')
def ge_filter(value, arg):
    """Return if the float representation of value is greater than or equal to arg."""
    return _cond_helper(operator.ge, (value, arg))


class LinkObject(template.Node):
    """Helper class for do_link_object()."""
    
    def __init__(self, obj):
        super(LinkObject, self).__init__()
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


class PrinterChoiceNode(template.Node):
    
    def __init__(self):
        self.current_printer = template.Variable('printer_choice')
        self.printer_list = template.Variable('printer_choice_list')
    
    def render(self, context):
        try:
            current_printer = self.current_printer.resolve(context)
        except template.VariableDoesNotExist:
            current_printer = None
        try:
            printer_list = self.printer_list.resolve(context)
        except template.VariableDoesNotExist:
            printer_list = ['NullPrinter']
        options = []
        for printer in printer_list:
            if printer == current_printer:
                options.append('<option value="%s" selected>%s</option>' % (printer, printer))
            else:
                options.append('<option value="%s">%s</option>' % (printer, printer))
        return '<select name="printer_choice">%s</select>' % ('\n'.join(options))


@register.tag
def printer_choice(dummy, token):
    """Display a simple printer choice dialog.
    
    This is meant to be used in conjunction with hudjango.PrinterChooser. It expects the 
    variables printer_choice and printer_choice_list to be available in the context.
    PrinterChooser.update_context can do that automatically. For futher information see the
    documentation of hudjango.PrinterChooser."""
    
    try:
        dummy = token.split_contents()
    except ValueError:
        raise template.TemplateSyntaxError("%r tag requires no arguments" % token.contents.split()[0])
    return PrinterChoiceNode()


class ImageLink(template.Node):
    """Helper class for rendering do_imageid()."""
    
    def __init__(self, obj, options):
        global huimages
        if huimages is None:
            import huimages
        super(ImageLink, self).__init__()
        self.obj = obj
        self.options = options
    
    def render(self, context):
        """Called when the page is actually rendered."""
        obj = resolve_variable(self.obj, context)
        imageid = getattr(obj, 'name', obj)
        if not imageid:
            return ''
        if self.options.get('urlonly', False):
            return unicode(huimages.imageurl(imageid))
        else:
            if self.options.get('nolink', False):
                return huimages.scaled_tag(imageid, self.options.get('size', '1024x768'))
            else:
                return unicode('<a class="imagelink" href="%s">%s</a>' % (huimages.imageurl(imageid),
                    huimages.scaled_tag(imageid, self.options.get('size', '1024x768'))))
    

def do_imageid(dummy, token):
    """Renders an Imagetag by ImageID. See pydoc huimages for information about ImageID.
       
       Syntax: {% imageid <imageid> <size> [nolink] [urlonly] %}
       
       See huimages for further Documentation on size.
       
       Example::
       
           {% imageid spare.bild "320x240" %} 
           <a class="imagelink" href="http://i.hdimg.net/o/TZGBY4PX2BXMKXXGNMYHZBVYZXSJBOLT01.jpeg"><img src="http://i.hdimg.net/320x240/TZGBY4PX2BXMKXXGNMYHZBVYZXSJBOLT01.jpeg" /></a>
           
           {% imageid "DEQOQMIPRJPPTAKLE3NQY5BTMMNTFGG201" "320x240" nolink %} 
           <img src="http://i.hdimg.net/320x240/DEQOQMIPRJPPTAKLE3NQY5BTMMNTFGG201.jpeg" />
           
           {% imageid spare.bild.name "150x150!" urlonly %} 
           http://i.hdimg.net/150x150!/TZGBY4PX2BXMKXXGNMYHZBVYZXSJBOLT01.jpeg
    """
    options = {'urlonly': False, 'nolink': False, 'size': '1024x768'}
    try:
        tokens = list(smart_split(token.contents))
        dummy, obj = tokens[:2]
        if len(tokens) > 2:
            options['size'] = tokens[2].strip('"\'')
        for option in tokens[2:]:
            if option.strip('"\'') == 'urlonly':
                options['urlonly'] = True
            if option.strip('"\'') == 'nolink':
                options['nolink'] = True
    except ValueError:
        raise template.TemplateSyntaxError, "%r tag requires a single argument" % token.contents.split()[0]
    return ImageLink(obj, options)
register.tag('imageid', do_imageid)


if __name__ == '__main__':
    import doctest
    doctest.testmod()
