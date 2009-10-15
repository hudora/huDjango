#testdefaulting - unit tests for defaulting.py

import unittest
import defaulting
from random import random
from django.dispatch import dispatcher


class emptyo(object):
    "Just sits there to have attributes assigned to it"
    pass


class TestDefaulting(unittest.TestCase):
    """Test Defaultin."""

    def setUp(self):
        """Create a few DefaultingCharFields."""

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
    
    def testInternalType(self):
        self.assertEqual("CharField", self.dcf.get_internal_type())
    

suite = unittest.TestLoader().loadTestsFromTestCase(TestDefaulting)

if __name__ == '__main__':
    unittest.main()
