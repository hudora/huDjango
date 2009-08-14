#testdefaulting - unit tests for defaulting.py

import unittest
import defaulting
from random import random
from django.dispatch import dispatcher

class emptyo(object):
    "Just sits there to have attributes assigned to it"
    pass

class TestDefaulting(unittest.TestCase):
    def setUp(self):
        self.dcfValue = random()
        self.dcf = defaulting.DefaultingCharField(self.dcfValue)
        self.dcf2 = defaulting.DefaultingCharField()
        
        self.__class__._meta = emptyo()
        def add_field(f):
            pass
        self.__class__._meta.add_field = add_field
        self.__class__._meta.module_name = "testaudit"
        self.__class__._meta.object_name = "TestUpdatedByField"
    
    def testInit(self):
        self.assertEqual(self.dcfValue, self.dcf.default_from_field)
        self.assert_(self.dcf2.default_from_field is None)
        self.assert_(isinstance(self.dcf, defaulting.DefaultingCharField))
    
    def testSetDefault(self):
        self.dcf._set_default(random())
        self.assertEqual(self.dcfValue, self.dcf.default_from_field)
        r = random()
        self.dcf2._set_default(r)
        self.assertEqual(r, self.dcf2.default_from_field)
    
    def testInternalType(self):
        self.assertEqual("CharField", self.dcf.get_internal_type())
    
    def testContributeToClass(self):
        l = len(dispatcher.connections)
        self.dcf.contribute_to_class(self.__class__, 'testing')
        self.assertEqual(l+1, len(dispatcher.connections))

suite = unittest.TestLoader().loadTestsFromTestCase(TestDefaulting)

if __name__ == '__main__':
    unittest.main()
