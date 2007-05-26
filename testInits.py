import unittest

class TestInits(unittest.TestCase):
    def testMiddlewareInit(self):
        import middleware
        self.assert_(str(middleware).startswith("<module 'middleware' from ") and str(middleware).endswith("middleware/__init__.pyc'>"))

    def testFieldsInit(self):
        import fields
        self.assert_(str(fields).startswith("<module 'fields' from ") and str(fields).endswith("fields/__init__.pyc'>"))

suite = unittest.TestLoader().loadTestsFromTestCase(TestInits)

if __name__ == '__main__':
    unittest.main()
