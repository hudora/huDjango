#testall.py - run all test cases

import unittest

import testInits
import middleware.testthreadlocals
import fields.testdefaulting
import fields.testscalingimagefield

tests = [testInits.suite, middleware.testthreadlocals.suite, 
         fields.testdefaulting.suite, 
         fields.testscalingimagefield.suite]
suite = unittest.TestSuite(tests)

if __name__ == '__main__':
    unittest.TextTestRunner(verbosity=3).run(suite)
