# encoding: utf-8

"""Image field which scales images on demand.

This acts like Django's ImageField but in addition can scale images on demand. Scaled Images are put in
<settings.MEDIA_ROOT>/,/<originalpath>. The avialable scaling factors are hardcoded in the dictionary _sizes.
If the dimensions there are followed by an '!' this means the images should be cropped to exactly this size.
Without this the images are scaled to fit in the given size without changing the aspect ratio of the image.

Scaled versions of the images are generated on the fly using PIL and then kept arround in the Filesystem. 

Given a model like

class Image(models.Model):
    path       = ScaledImageField(verbose_name='Datei', upload_to='-/product/image')
    [...]

you can do  the following:

>>> img.path  
'-/product/image/0e99d6be8ec0259df920c2d273d1ad6f.jpg'
>>>img.get_path_url()
'/media/-/product/image/0e99d6be8ec0259df920c2d273d1ad6f.jpg'
>>> img.get_path_size()
417119L
>>> img.get_path_width()
1584
>>> img.get_path_height()
2889

All well known metods from ImageField are supported. The new functionality is available via img.path_scaled - this returns an
Imagescaler instance beeing able to play some nifty tricks:

>>> img.path_scaled().svga()
'/,/-/product/image/0e99d6be8ec0259df920c2d273d1ad6f.jpg/svga.jpeg'
>>> img.path_scaled().svga_path()
'/usr/local/web/media/,/-/product/image/0e99d6be8ec0259df920c2d273d1ad6f.jpg/svga.jpeg'
>>> img.path_scaled().svga_dimensions()
(328, 600)
>>> img.path_scaled().svga_tag()
'<img src="/,/-/product/image/0e99d6be8ec0259df920c2d273d1ad6f.jpg/svga.jpeg" width="328" height="600" />'
>>> img.path_scaled().thumb_dimensions()
(50, 91)
>>> img.path_scaled().square_dimensions()
(75, 76)

Created August 2006 by Maximillian Dornseif. Updated in early 2009.
Consider it BSD licensed.
"""

import Image 
import os
import urlparse
from django.conf import settings
from django.db.models import ImageField
from django.utils.functional import curry
from django.utils.html import escape 
from django.utils.safestring import mark_safe 

_sizes = {'mini': "23x40",
          'thumb': "50x200", 
          'sidebar': "179x600",
          'small': "240x160",
          'medium': "480x320", 
          'full': "477x800",
          'svga': "800x600", 
          'xvga': "1024x768",
          'square': "75x75!"} 


def _scaleImage(width, height, image):
    """
    This function will scale an image to a given bounding box. Image
    aspect ratios will be conserved and so there might be blank space
    at two sides of the image if the ratio isn't identical to that of
    the bounding box.
    """
    #from http://simon.bofh.ms/cgi-bin/trac-django-projects.cgi/file/stuff/branches/magic-removal/image.py
    lfactor = 1
    width, height = int(width), int(height)
    (xsize, ysize) = image.size
    if xsize > width and ysize > height:
        lfactorx = float(width) / float(xsize)
        lfactory = float(height) / float(ysize)
        lfactor = min(lfactorx, lfactory)
    elif xsize > width:
        lfactor = float(width) / float(xsize)
    elif ysize > height:
        lfactor = float(height) / float(ysize)
    res = image.resize((int(float(xsize) * lfactor), int(float(ysize) * lfactor)), Image.ANTIALIAS)
    return res


def _cropImage(width, height, image):
    """
    This will crop the largest block out of the middle of an image
    that has the same aspect ratio as the given bounding box. No
    blank space will be in the thumbnail, but the image isn't fully
    visible due to croping.
    """
    #from http://simon.bofh.ms/cgi-bin/trac-django-projects.cgi/file/stuff/branches/magic-removal/image.py
    # moderately modified
    width, height = int(width), int(height)
    lfactor = 1
    (xsize, ysize) = image.size
    if xsize > width and ysize > height:
        lfactorx = float(width) / float(xsize)
        lfactory = float(height) / float(ysize)
        lfactor = max(lfactorx, lfactory)
    newx = int(float(xsize) * lfactor)
    newy = int(float(ysize) * lfactor)
    res = image.resize((newx, newy), Image.ANTIALIAS)
    leftx = 0
    lefty = 0
    rightx = newx
    righty = newy
    if newx > width:
        leftx += (newx - width) / 2
        rightx -= (newx - width) / 2
    elif newy > height:
        lefty += (newy - height) / 2
        righty -= (newy - height) / 2
    res = res.crop((leftx, lefty, rightx, righty))
    return res


class Imagescaler(object):
    """Class whose instances scale an image on the fly to desired properties.
    
    For each set of dimensions defined in _sizes imagescaler has a set of functions, e.g. for 'small':
    
    o.small() = return the URL of the small version of the image
    o.small_path() - return the absolute  pathe in the filesystem for the  image
    o.small_dimensions() - return (width,  heigth)
    o.small_tag() - return a complete image tag for use in XHTML
    
    >>> img.path_scaled().svga()
    '/,/-/product/image/0e99d6be8ec0259df920c2d273d1ad6f.jpg_svga.jpeg'
    >>> img.path_scaled().svga_path()
    '/usr/local/web/media/,/-/product/image/0e99d6be8ec0259df920c2d273d1ad6f.jpg_svga.jpeg'
    >>> img.path_scaled().svga_dimensions()
    (328, 600)
    >>> img.path_scaled().svga_tag()
    '<img src="/,/-/product/image/0e99d6be8ec0259df920c2d273d1ad6f.jpg_svga.jpeg" width="328" height="600" />'
    """

    def __init__(self, field, obj):
        self.field = field
        self.parent_obj = obj
        self.original_image = getattr(self.parent_obj, self.field.attname)
        self.original_image_path = os.path.join(settings.MEDIA_ROOT, str(self.original_image))
        self.mangled_name = str(self.original_image) # md5.new('sehkr1tt-%s-%r-%r' % (str(self.original_image), time.time(), id(self))).hexdigest()
        self.scaled_image_base = os.path.join(settings.MEDIA_ROOT, ',', self.mangled_name)
        self.broken_image = None
        # if broken.gif exists we send that if there are any problems during scaling
        if not os.path.exists(self.original_image_path):
            self.broken_image = os.path.join(settings.MEDIA_ROOT, 'broken.gif') 
        for size in _sizes:
            setattr(self, '%s_path' % (size), curry(self.scaled_filename, size))
            setattr(self, '%s' % (size), curry(self.scaled_url, size))
            setattr(self, '%s_dimensions' % (size), curry(self.scaled_dimensions, size))
            setattr(self, '%s_tag' % (size), curry(self.scaled_tag, size))

    def scaled_filename(self, size='thumb'):
        """Scales an image according to 'size' and returns the filename of the scaled image."""
        if self.broken_image:
            return self.broken_image
        outpath = "%s_%s.jpeg" % (self.scaled_image_base, size)
        if not os.path.exists(outpath):
            if size not in _sizes:
                width, height = size.split('x')
            else:
                width, height = _sizes[size].split('x')
            img = Image.open(self.original_image_path)
            if height.endswith('!'):
                height = height.strip('!')
                img = _cropImage(width, height, img)
            else:
                img = _scaleImage(width, height, img)
            if img.mode != "RGB":
                img = img.convert("RGB")
            img.save(outpath, "JPEG")
        return outpath

    def scaled_url(self, size='thumb'):
        """Scales an image according to 'size' and returns the URL of the scaled image."""
        if not self.original_image:
            return ''
        outpath = self.scaled_filename(size)
        url = outpath[len(settings.MEDIA_ROOT):]
        if url.startswith('/'):
            url = url[1:]
        return urlparse.urljoin(settings.MEDIA_URL, url).replace('\\', '/')
    
    def scaled_dimensions(self, size='thumb'):
        """Scales an image according to 'size' and returns the dimensions."""
        if not self.original_image:
            return None
        if size.endswith('!'):
            return [int(i) for i in _sizes[size].split('x')]
        return Image.open(self.scaled_filename(size)).size
    
    def scaled_tag(self, size='thumb', *args, **kwargs):
        """Scales an image according to 'size' and returns an XHTML tag for that image.
        
        Additional keyword arguments are added as attributes to  the <img> tag.
        
        >>> img.path_scaled().svga_tag(alt='neu')
        '<img src="/,/-/product/image/0ead6f.jpg/svga.jpeg" width="328" height="600" alt="neu"/>'
        """
        if not self.original_image:
            return ''
        ret = ['<img src="%s"' % escape(self.scaled_url(size))]
        try:
            ret.append('width="%d" height="%d"' % self.scaled_dimensions(size))
        except:
            ret.append('width="50" height="50" alt="Fehler bei der Groessenberechnung" ')
        ret.extend(args)
        for key, val in kwargs.items():
            ret.append('%s="%s"' % (escape(key), escape(val)))
        ret.append('/>')
        return mark_safe(' '.join(ret))


class ScalingImageField(ImageField):
    """This acts like Django's ImageField but in addition can scale images on demand by providing an
    ImageScaler object.
    
    >>> img.path_scaled().svga()
    '/,/-/product/image/0e99d6be8ec0259df920c2d273d1ad6f.jpg/svga.jpeg'
    """

    def __init__(self, verbose_name=None, name=None, width_field=None, height_field=None, auto_rename=True,
                 **kwargs):
        """Inits the ScalingImageField."""
        super(ScalingImageField, self).__init__(verbose_name, name, width_field, height_field, **kwargs)

    def contribute_to_class(self, cls, name):
        """Adds field-related functions to the model."""
        super(ScalingImageField, self).contribute_to_class(cls, name)
        setattr(cls, '%s_scaled' % self.name, curry(Imagescaler, self))

    def get_internal_type(self):
        return 'FileField'
