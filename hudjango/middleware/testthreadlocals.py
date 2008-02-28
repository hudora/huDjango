import unittest
from thread import start_new_thread as launch
import threadlocals
from random import random

class TestThreadLocals(unittest.TestCase):
    def testLocalImplementation(self):
        lo = threadlocals.local()
        lo.foo = "bar"
        self.assertEqual(lo.foo, "bar")
        def fetchfoo():
            return lo.foo
        self.assertEqual(fetchfoo(), "bar")
        launch(self.assertRaises, (AttributeError, fetchfoo))
        def getsetlocal():
            lo.foo = 'bat'
            self.assertEqual(lo.foo, "bat")
        launch(getsetlocal, ())
        self.assertEqual(lo.foo, "bar")
        
    
    def testGetSetLocalUser(self):
        self.assert_(threadlocals.get_current_user() is None)
        val = random()
        threadlocals.set_current_user(val)
        self.assertEquals(val, threadlocals.get_current_user())
    
    def testGetSetRemoteIP(self):
        self.assert_(threadlocals.get_remote_ip() is None)
        val = random()
        threadlocals.set_remote_ip(val)
        self.assertEquals(val, threadlocals.get_remote_ip())
        
    def testThreadLocalsClass(self):
        request = threadlocals.ThreadLocals() #almost any class except object() would work
        request.user = user = random()
        request.META = {}
        request.META['REMOTE_ADDR'] = addr = random()
        threadlocals.ThreadLocals().process_request(request)
        self.assertEqual(user, threadlocals.get_current_user())
        self.assertEqual(addr, threadlocals.get_remote_ip())

suite = unittest.TestLoader().loadTestsFromTestCase(TestThreadLocals)

if __name__ == '__main__':
    unittest.main()
