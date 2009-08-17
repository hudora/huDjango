#testall.py - run all unittests test cexcept the ones in the test directory ...

import unittest

# ensure coverage sees even modules without tests
import hudjango.auth.backends
import hudjango.auth.decorators
import hudjango.fields.testdefaulting
import hudjango.fields.testscalingimagefield
import hudjango.middleware.clienttrack
import hudjango.middleware.testthreadlocals
# need to figure out huImages dependency
#import hudjango.storage
#import hudjango.templatetags.hudjango

tests = [hudjango.middleware.testthreadlocals.suite,
         hudjango.fields.testdefaulting.suite,
         hudjango.fields.testscalingimagefield.suite]
suite = unittest.TestSuite(tests)

if __name__ == '__main__':
    unittest.TextTestRunner(verbosity=3).run(suite)
