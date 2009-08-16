#testall.py - run all unittests test cexcept the ones in the test directory ...

import unittest

import testInits
import middleware.testthreadlocals
import fields.testdefaulting
import fields.testscalingimagefield

tests = [middleware.testthreadlocals.suite, 
         fields.testdefaulting.suite, 
         fields.testscalingimagefield.suite]
suite = unittest.TestSuite(tests)

if __name__ == '__main__':
    unittest.TextTestRunner(verbosity=3).run(suite)
