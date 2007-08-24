#! /usr/bin/env python
"""Test script for the whichdb module
   based on test_anydbm.py
"""

import os
import test.test_support
import unittest
import whichdb
import anydbm
import tempfile
import glob
from test.test_anydbm import delete_files, dbm_iterator

_fname = test.test_support.TESTFN

class WhichDBTestCase(unittest.TestCase):
    # Actual test methods are added to namespace
    # after class definition.
    def __init__(self, *args):
        unittest.TestCase.__init__(self, *args)

    def test_whichdb(self):
        for module in dbm_iterator():
            # Check whether whichdb correctly guesses module name
            # for databases opened with "module" module.
            # Try with empty files first
            name = module.__name__
            if name == 'dumbdbm':
                continue   # whichdb can't support dumbdbm
            f = module.open(_fname, 'c')
            f.close()
            self.assertEqual(name, whichdb.whichdb(_fname))
            # Now add a key
            f = module.open(_fname, 'w')
            f[b"1"] = b"1"
            # and test that we can find it
            assert b"1" in f
            # and read it
            assert f[b"1"] == b"1"
            f.close()
            self.assertEqual(name, whichdb.whichdb(_fname))

    def tearDown(self):
        delete_files()

    def setUp(self):
        delete_files()


def test_main():
    try:
        test.test_support.run_unittest(WhichDBTestCase)
    finally:
        delete_files()

if __name__ == "__main__":
    test_main()
