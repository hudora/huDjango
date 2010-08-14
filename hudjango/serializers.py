#!/usr/bin/env python
# encoding: utf-8
"""
hudjango/serializers.py - serialize QuerySets or lit of objects to Excel/XLS.

http://docs.djangoproject.com/en/dev/topics/serialization/ is inspiration for this.

Created by Maximillian Dornseif on 2009-08-17.
Copyright (c) 2009 HUDORA. All rights reserved.
"""


import django.db.models.fields.files
import django.contrib.sites.models
import datetime
import types
import xlwt
from cStringIO import StringIO

xlwt.UnicodeUtils.DEFAULT_ENCODING = 'utf-8'


def _write_row(worksheet, row, pos_row):
    """Write a row to the current worksheet."""
    col = 0
    for cell in row:
        if isinstance(cell, list):
            worksheet.write(pos_row, col, ', '.join(cell))
        elif isinstance(cell, datetime.datetime):
            worksheet.write(pos_row, col, cell.strftime('%Y-%m-%d %H:%M'))
        # elif isinstance(cell, django.db.models.fields.files.ImageFieldFile):
        #     cellcontent = ''
        #     if getattr(cell, 'name', None):
        #         cellcontent = xlwt.Formula('HYPERLINK("%s";"%s")'
        #                                    % (huimages.imageurl(getattr(cell, 'name')), "Bild"))
        #         worksheet.write(pos_row, col, cellcontent)
        else:
            worksheet.write(pos_row, col, cell)
        col += 1
    return pos_row + 1


def queryset_to_xls(queryset, fields=None, headings=None):
    """Takes a Django queryset or a list of Objects and returns an XLS Sheet.

    Returns '' if the Queryset is empty."""

    if not queryset:
        return ''
    if not headings:
        headings = {}

    if not fields and hasattr(queryset, 'model'):
        fields = sorted([field.name for field in queryset.model._meta.fields])
    if not fields and queryset and hasattr(queryset[0], '_meta'):
        fields = sorted([field.name for field in queryset[0]._meta.fields])
    assert fields, "must be called with a list of fieldnames or a Queryset"

    workbook = xlwt.Workbook()

    # 1. Worksheet, ausführlich
    worksheet = workbook.add_sheet(u'Details')
    pos_row = 0

    # write headings
    headingrow = ['']
    for name in fields:
        headingrow.append(headings.get(name, name))
    pos_row = _write_row(worksheet, headingrow, pos_row)

    for obj in list(queryset):
        absurl = obj.get_absolute_url()
        if not absurl.startswith('http://'):
            absurl = 'http://%s%s' % (django.contrib.sites.models.Site.objects.get_current().domain, absurl)
        linktext = unicode(obj).replace('"', '') # Extremly curude but get's the job done
        row = [xlwt.Formula('HYPERLINK("%s";"%s")' % (absurl, linktext))]
        for name in fields:
            if hasattr(getattr(obj, name), '__call__'):
                # call 'name' is possible ...
                row.append(getattr(obj, name)())
            else:
                # if not, use value
                row.append(getattr(obj, name))
        pos_row = _write_row(worksheet, row, pos_row)
    pos_row = _write_row(worksheet, [u'Stand:', unicode(datetime.datetime.now())], pos_row)

    buf = StringIO()
    workbook.save(buf)
    return buf.getvalue()
