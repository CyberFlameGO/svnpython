"""Tests for 'site'.

Tests assume the initial paths in sys.path once the interpreter has begun
executing have not been removed.

"""
import unittest
import sys
import test
import os
from copy import copy, deepcopy

from test.test_support import run_unittest, TESTFN

import sysconfig
from sysconfig import (get_paths, get_platform, get_config_vars,
                       get_path, get_path_names, _INSTALL_SCHEMES)

class TestSysConfig(unittest.TestCase):

    def setUp(self):
        """Make a copy of sys.path"""
        super(TestSysConfig, self).setUp()
        self.sys_path = sys.path[:]
        self.makefile = None
        # patching os.uname
        if hasattr(os, 'uname'):
            self.uname = os.uname
            self._uname = os.uname()
        else:
            self.uname = None
            self._uname = None
        os.uname = self._get_uname
        # saving the environment
        self.name = os.name
        self.platform = sys.platform
        self.version = sys.version
        self.sep = os.sep
        self.join = os.path.join
        self.isabs = os.path.isabs
        self.splitdrive = os.path.splitdrive
        self._config_vars = copy(sysconfig._CONFIG_VARS)
        self.old_environ = deepcopy(os.environ)

    def tearDown(self):
        """Restore sys.path"""
        sys.path[:] = self.sys_path
        if self.makefile is not None:
            os.unlink(self.makefile)
        self._cleanup_testfn()
        if self.uname is not None:
            os.uname = self.uname
        else:
            del os.uname
        os.name = self.name
        sys.platform = self.platform
        sys.version = self.version
        os.sep = self.sep
        os.path.join = self.join
        os.path.isabs = self.isabs
        os.path.splitdrive = self.splitdrive
        sysconfig._CONFIG_VARS = copy(self._config_vars)
        for key, value in self.old_environ.items():
            if os.environ.get(key) != value:
                os.environ[key] = value

        for key in os.environ.keys():
            if key not in self.old_environ:
                del os.environ[key]

        super(TestSysConfig, self).tearDown()

    def _set_uname(self, uname):
        self._uname = uname

    def _get_uname(self):
        return self._uname

    def _cleanup_testfn(self):
        path = test.test_support.TESTFN
        if os.path.isfile(path):
            os.remove(path)
        elif os.path.isdir(path):
            shutil.rmtree(path)

    def test_get_path_names(self):
        self.assertEquals(get_path_names(), sysconfig._SCHEME_KEYS)

    def test_get_paths(self):
        # XXX make it os independant
        scheme = get_paths()
        wanted = [('data', '/usr/local'),
            ('include', '/Users/tarek/Dev/svn.python.org/tarek_sysconfig/Include'),
            ('platinclude', '.'),
            ('platlib', '/usr/local/lib/python'),
            ('platstdlib', '/usr/local/lib/python'),
            ('purelib', '/usr/local/lib/python'),
            ('scripts', '/usr/local/bin'),
            ('stdlib', '/usr/local/lib/python')]

        scheme = scheme.items()
        scheme.sort()
        self.assertEquals(scheme, wanted)

    def test_get_path(self):
        # xxx make real tests here
        for scheme in _INSTALL_SCHEMES:
            for name in _INSTALL_SCHEMES[scheme]:
                res = get_path(name, scheme)

    def test_get_config_vars(self):
        cvars = get_config_vars()
        self.assertTrue(isinstance(cvars, dict))
        self.assertTrue(cvars)

    def test_get_platform(self):
        # windows XP, 32bits
        os.name = 'nt'
        sys.version = ('2.4.4 (#71, Oct 18 2006, 08:34:43) '
                       '[MSC v.1310 32 bit (Intel)]')
        sys.platform = 'win32'
        self.assertEquals(get_platform(), 'win32')

        # windows XP, amd64
        os.name = 'nt'
        sys.version = ('2.4.4 (#71, Oct 18 2006, 08:34:43) '
                       '[MSC v.1310 32 bit (Amd64)]')
        sys.platform = 'win32'
        self.assertEquals(get_platform(), 'win-amd64')

        # windows XP, itanium
        os.name = 'nt'
        sys.version = ('2.4.4 (#71, Oct 18 2006, 08:34:43) '
                       '[MSC v.1310 32 bit (Itanium)]')
        sys.platform = 'win32'
        self.assertEquals(get_platform(), 'win-ia64')

        # macbook
        os.name = 'posix'
        sys.version = ('2.5 (r25:51918, Sep 19 2006, 08:49:13) '
                       '\n[GCC 4.0.1 (Apple Computer, Inc. build 5341)]')
        sys.platform = 'darwin'
        self._set_uname(('Darwin', 'macziade', '8.11.1',
                   ('Darwin Kernel Version 8.11.1: '
                    'Wed Oct 10 18:23:28 PDT 2007; '
                    'root:xnu-792.25.20~1/RELEASE_I386'), 'i386'))
        get_config_vars()['MACOSX_DEPLOYMENT_TARGET'] = '10.3'
        os.environ['MACOSX_DEPLOYMENT_TARGET'] = '10.3'

        get_config_vars()['CFLAGS'] = ('-fno-strict-aliasing -DNDEBUG -g '
                                       '-fwrapv -O3 -Wall -Wstrict-prototypes')

        self.assertEquals(get_platform(), 'macosx-10.3-i386')

        # macbook with fat binaries (fat, universal or fat64)
        os.environ['MACOSX_DEPLOYMENT_TARGET'] = '10.4'
        get_config_vars()['CFLAGS'] = ('-arch ppc -arch i386 -isysroot '
                                       '/Developer/SDKs/MacOSX10.4u.sdk  '
                                       '-fno-strict-aliasing -fno-common '
                                       '-dynamic -DNDEBUG -g -O3')

        self.assertEquals(get_platform(), 'macosx-10.4-fat')

        get_config_vars()['CFLAGS'] = ('-arch x86_64 -arch i386 -isysroot '
                                       '/Developer/SDKs/MacOSX10.4u.sdk  '
                                       '-fno-strict-aliasing -fno-common '
                                       '-dynamic -DNDEBUG -g -O3')

        self.assertEquals(get_platform(), 'macosx-10.4-intel')

        get_config_vars()['CFLAGS'] = ('-arch x86_64 -arch ppc -arch i386 -isysroot '
                                       '/Developer/SDKs/MacOSX10.4u.sdk  '
                                       '-fno-strict-aliasing -fno-common '
                                       '-dynamic -DNDEBUG -g -O3')
        self.assertEquals(get_platform(), 'macosx-10.4-fat3')

        get_config_vars()['CFLAGS'] = ('-arch ppc64 -arch x86_64 -arch ppc -arch i386 -isysroot '
                                       '/Developer/SDKs/MacOSX10.4u.sdk  '
                                       '-fno-strict-aliasing -fno-common '
                                       '-dynamic -DNDEBUG -g -O3')
        self.assertEquals(get_platform(), 'macosx-10.4-universal')

        get_config_vars()['CFLAGS'] = ('-arch x86_64 -arch ppc64 -isysroot '
                                       '/Developer/SDKs/MacOSX10.4u.sdk  '
                                       '-fno-strict-aliasing -fno-common '
                                       '-dynamic -DNDEBUG -g -O3')

        self.assertEquals(get_platform(), 'macosx-10.4-fat64')

        for arch in ('ppc', 'i386', 'x86_64', 'ppc64'):
            get_config_vars()['CFLAGS'] = ('-arch %s -isysroot '
                                           '/Developer/SDKs/MacOSX10.4u.sdk  '
                                           '-fno-strict-aliasing -fno-common '
                                           '-dynamic -DNDEBUG -g -O3'%(arch,))

            self.assertEquals(get_platform(), 'macosx-10.4-%s'%(arch,))

        # linux debian sarge
        os.name = 'posix'
        sys.version = ('2.3.5 (#1, Jul  4 2007, 17:28:59) '
                       '\n[GCC 4.1.2 20061115 (prerelease) (Debian 4.1.1-21)]')
        sys.platform = 'linux2'
        self._set_uname(('Linux', 'aglae', '2.6.21.1dedibox-r7',
                    '#1 Mon Apr 30 17:25:38 CEST 2007', 'i686'))

        self.assertEquals(get_platform(), 'linux-i686')

        # XXX more platforms to tests here


def test_main():
    run_unittest(TestSysConfig)

if __name__ == "__main__":
    test_main()
