#testall.py - run all unittests test cexcept the ones in the test directory ...

import unittest

import hudjango.middleware.testthreadlocals
import hudjango.fields.testdefaulting
import hudjango.fields.testscalingimagefield

tests = [hudjango.middleware.testthreadlocals.suite,
         hudjango.fields.testdefaulting.suite,
         hudjango.fields.testscalingimagefield.suite]
suite = unittest.TestSuite(tests)

if __name__ == '__main__':
    unittest.TextTestRunner(verbosity=3).run(suite)
