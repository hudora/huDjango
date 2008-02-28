#test the audit.py classes and so forth

import audit
import unittest
from random import random
from django.dispatch import dispatcher

class emptyo(object):
    "Just sits there to have attributes assigned to it"
    pass

class TestUpdatedByField(unittest.TestCase):
    def setUp(self):
        self.ubf = audit.UpdatedByField()
        self.user = emptyo()
        self.user.id = random()
        audit.threadlocals.set_current_user(self.user)
        self.ip = random()
        audit.threadlocals.set_remote_ip(self.ip)
        self.__class__._meta = emptyo()
        def add_field(f):
        	pass
        self.__class__._meta.add_field = add_field
        self.__class__._meta.module_name = "testaudit"
        self.__class__._meta.object_name = "TestUpdatedByField"
    
    def testInit(self):
        self.assert_(isinstance(self.ubf, audit.UpdatedByField))
    
    def testInternalType(self):
        self.assertEqual(self.ubf.get_internal_type(), "ForeignKey")
    
    def testSetUser(self):
        e = emptyo()
        self.ubf._set_user(e)
        self.assertEqual(getattr(e, self.ubf.attname), self.user.id)
        
        #also test that the default call works
        self.ubf._set_user()
        
    def testContributeToClass(self):
        l = len(dispatcher.connections)
        self.ubf.contribute_to_class(self.__class__, 'testing')
        self.assertEqual(l+1, len(dispatcher.connections))

class TestCreatedByField(unittest.TestCase):
    def setUp(self):
        self.ubf = audit.CreatedByField()
        self.user = emptyo()
        self.user.id = random()
        audit.threadlocals.set_current_user(self.user)
        self.ip = random()
        audit.threadlocals.set_remote_ip(self.ip)
        
        self.__class__._meta = emptyo()
        def add_field(f):
        	pass
        self.__class__._meta.add_field = add_field
        self.__class__._meta.module_name = "testaudit"
        self.__class__._meta.object_name = "TestUpdatedByField"
    
    def testInit(self):
        self.assert_(isinstance(self.ubf, audit.CreatedByField))
    
    def testInternalType(self):
        self.assertEqual(self.ubf.get_internal_type(), "ForeignKey")
    
    def testSetUser(self):
        e = emptyo()
        e.id = random()
        self.ubf._set_user(e)
        self.assertEqual(getattr(e, self.ubf.attname), self.user.id)
        
        #also test that the default call works
        self.ubf._set_user()
        
    def testContributeToClass(self):
        l = len(dispatcher.connections)
        self.ubf.contribute_to_class(self.__class__, 'testing')
        self.assertEqual(l+1, len(dispatcher.connections))

class TestUpdatedByIPField(unittest.TestCase):
    def setUp(self):
        self.ipf = audit.UpdatedByIPField()
        
        self.__class__._meta = emptyo()
        def add_field(f):
            pass
        self.__class__._meta.add_field = add_field
        self.__class__._meta.module_name = "testaudit"
        self.__class__._meta.object_name = "TestUpdatedByField"
        
    def testInit(self):
        self.assert_(isinstance(self.ipf, audit.UpdatedByIPField))
    
    def testInternalType(self):
        self.assertEqual(self.ipf.get_internal_type(), "IPAddressField")
    
    def testSetIP(self):
        e = emptyo()
        self.ipf._set_ip(e)
        self.assertEqual(getattr(e, self.ubf.attname), self.ip)
        
        #also test that the default call works
        self.ubf._set_ip()
        
    def testContributeToClass(self):
        l = len(dispatcher.connections)
        self.ipf.contribute_to_class(self.__class__, 'testing')
        self.assertEqual(l+1, len(dispatcher.connections))

class TestCreatedByIPField(unittest.TestCase):
    def setUp(self):
        self.ipf = audit.CreatedByIPField()
        
        self.__class__._meta = emptyo()
        def add_field(f):
        	pass
        self.__class__._meta.add_field = add_field
        self.__class__._meta.module_name = "testaudit"
        self.__class__._meta.object_name = "TestUpdatedByField"
        
    def testInit(self):
        self.assert_(isinstance(self.ipf, audit.CreatedByIPField))
    
    def testInternalType(self):
        self.assertEqual(self.ipf.get_internal_type(), "IPAddressField")
    
    def testSetIP(self):
        e = emptyo()
        e.id = False
        self.ipf._set_ip(e)
        self.assertEqual(getattr(e, self.ubf.attname), self.ip)
        
        #not much should happen if e.id = exists
        e.id = True
        self.ipf._set_ip(e)		
        
        #also test that the default call works
        self.ubf._set_ip()
        
    def testContributeToClass(self):
        l = len(dispatcher.connections)
        self.ipf.contribute_to_class(self.__class__, 'testing')
        self.assertEqual(l+1, len(dispatcher.connections))

classes = [TestUpdatedByField, TestCreatedByField, TestUpdatedByIPField, TestCreatedByIPField]
suite = unittest.TestSuite([unittest.TestLoader().loadTestsFromTestCase(cls) for cls in classes])

if __name__ == '__main__':
    unittest.main()