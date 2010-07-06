# encoding: utf-8

from django import forms
from django.forms.util import flatatt
from django.utils.encoding import StrAndUnicode, force_unicode
from django.utils.safestring import mark_safe

class ReadOnly(forms.Widget):
    """
    "Read Only" Widget
    """

    def render(self, name, value, attrs=None):
        if value is None:
            value = ''
        final_attrs = self.build_attrs(attrs, type='hidden', name=name)
        if value != '':
            final_attrs['value'] = force_unicode(value)
        return mark_safe(u'<span>%s</span><input type="hidden" %s/>' % (value, flatatt(final_attrs)))
