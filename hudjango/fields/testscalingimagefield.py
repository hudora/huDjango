#testscalingimagefield.py - tests for scalingimagefield.py

import os
import re
import scalingimagefield as sif
import unittest
from django.conf import settings
from django.dispatch import dispatcher
from random import random

axb = re.compile(r"\d+x\d+")

class emptyo(object):
    "Just sits there to have attributes assigned to it"
    pass

class image(object):
    def __init__(self, x, y):
        self.size = (x, y)
    def resize(self, size, quality=1):
        self.size = size
        return self
    def crop(self, dimensions):
        leftx, lefty, rightx, righty = dimensions
        self.size = (rightx - leftx, righty - lefty)
        self.cropDims = dimensions
        return self

class TestSIF(unittest.TestCase):
    def setUp(self):
        self.bigimage = image(1280, 1024)
        self.smallimage = image(640, 480)
    
    def testModuleVars(self):
        for k, v in sif._sizes.iteritems():
            self.assert_(k.isalpha())
            self.assert_(axb.match(v))
    
    def test_ScaleImageConstrainY(self):
        self.assertEqual(sif._scaleImage(500, 300, self.bigimage).size, (375, 300))
    def test_scaleImageConstrainX(self):
        self.assertEqual(sif._scaleImage(300, 500, self.bigimage).size, (300, 240))
    
    def test_scaleImageGrow(self):
        self.assertEqual(sif._scaleImage(800, 600, self.smallimage).size, (640, 480))
    
    def test_cropImageTooBig(self):
        self.assertEqual(sif._cropImage(1280, 1024, self.smallimage).cropDims, (0, 0, 640, 480))
    
    def test_cropImageWaySmall(self):
        "docstring asserts we choose the centermost region"
        self.assertEqual(sif._cropImage(640, 480, self.bigimage).cropDims, (320, 272, 960, 752))
    
    def test_cropImageConstrainX(self):
        self.assertEqual(sif._cropImage(1024, 1024, self.bigimage).cropDims, (128, 0, 1152, 1024))
    
    def test_cropImageConstrainY(self):
        self.assertEqual(sif._cropImage(1280, 1000, self.bigimage).cropDims, (0, 12, 1280, 1012))

class TestImageScaler(unittest.TestCase):
    def setUp(self):
        self.path = str(random())
        field = emptyo()
        field.attname="image"
        parent = emptyo()
        parent.image = self.path
        self.imagescaler = sif.Imagescaler(field, parent)
    
    def testImageScalerInit(self):
        self.assert_(isinstance(self.imagescaler, sif.Imagescaler))
    
    def testImageScalerAttrs(self):
        self.assertEqual(self.path, self.imagescaler.original_image)
        self.assertEqual(os.path.join(settings.MEDIA_ROOT, self.path), self.imagescaler.original_image_path)
        self.assertEqual(os.path.join(settings.MEDIA_ROOT, ',', self.path), self.imagescaler.scaled_image_dir)
        
        for size in sif._sizes:
            for end in ['', '_path', '_dimensions', '_tag']:
                self.assert_(size + end in dir(self.imagescaler))
                self.assert_(callable(getattr(self.imagescaler, size + end)))
    
    def testImagescalerScaledFilename(self):
        self.assertEquals(self.imagescaler.scaled_filename(), 'broken.gif')
    
    def testImageScalerScaledURL(self):
        self.assertEquals(self.imagescaler.scaled_url(), 'broken.gif')
    
    def testImageScalerScaledDimensions(self):
        "broken.gif doesn't actually exist"
        self.assertRaises(IOError, self.imagescaler.scaled_dimensions)
    
    def testImageScalerScaledTag(self):
        "broken.gif doesn't actually exist"
        self.assertRaises(IOError, self.imagescaler.scaled_tag)

class TestScalingImageField(unittest.TestCase):
    def setUp(self):
        self.sif = sif.ScalingImageField()
        
        self.__class__._meta = emptyo()
        def add_field(f):
            pass
        self.__class__._meta.add_field = add_field
        self.__class__._meta.module_name = "testscalingimagefield"
        self.__class__._meta.object_name = "TestScalingImageField"
        self.__class__._get_FIELD_filename = None
        self.__class__._get_FIELD_url = None
        self.__class__._get_FIELD_size = None
        self.__class__._get_FIELD_width = None
        self.__class__._get_FIELD_height = None
    
    def testSIFInit(self):
        self.assert_(isinstance(self.sif, sif.ScalingImageField))
    
    def testSIF_saveNull(self):
        self.assert_(self.sif._save() is None)
    
    def testSIF_save(self):
        "the image doesn't exist so we should return none"
        e = emptyo()
        e.imagepath = './'
        self.assert_(self.sif._save(e) is None)
    
    def testSIFinternaltype(self):
        self.assertEqual(self.sif.get_internal_type(), "ImageField")
    
    def testSIFContributeToClass(self):
        l = len(dispatcher.connections)
        self.sif.contribute_to_class(self.__class__, 'testing')
        self.assertEqual(l+1, len(dispatcher.connections))

classes = [TestSIF, TestImageScaler, TestScalingImageField]
suite = unittest.TestSuite([unittest.TestLoader().loadTestsFromTestCase(cls) for cls in classes])

if __name__ == '__main__':
    unittest.main()
