import copyreg
import unittest

from test import support
from test.pickletester import ExtensionSaver

class C:
    pass


class WithoutSlots(object):
    pass

class WithWeakref(object):
    __slots__ = ('__weakref__',)

class WithPrivate(object):
    __slots__ = ('__spam',)

class WithSingleString(object):
    __slots__ = 'spam'

class WithInherited(WithSingleString):
    __slots__ = ('eggs',)


class CopyRegTestCase(unittest.TestCase):

    def test_class(self):
        self.assertRaises(TypeError, copyreg.pickle,
                          C, None, None)

    def test_noncallable_reduce(self):
        self.assertRaises(TypeError, copyreg.pickle,
                          type(1), "not a callable")

    def test_noncallable_constructor(self):
        self.assertRaises(TypeError, copyreg.pickle,
                          type(1), int, "not a callable")

    def test_bool(self):
        import copy
        self.assertEquals(True, copy.copy(True))

    def test_extension_registry(self):
        mod, func, code = 'junk1 ', ' junk2', 0xabcd
        e = ExtensionSaver(code)
        try:
            # Shouldn't be in registry now.
            self.assertRaises(ValueError, copyreg.remove_extension,
                              mod, func, code)
            copyreg.add_extension(mod, func, code)
            # Should be in the registry.
            self.assert_(copyreg._extension_registry[mod, func] == code)
            self.assert_(copyreg._inverted_registry[code] == (mod, func))
            # Shouldn't be in the cache.
            self.assert_(code not in copyreg._extension_cache)
            # Redundant registration should be OK.
            copyreg.add_extension(mod, func, code)  # shouldn't blow up
            # Conflicting code.
            self.assertRaises(ValueError, copyreg.add_extension,
                              mod, func, code + 1)
            self.assertRaises(ValueError, copyreg.remove_extension,
                              mod, func, code + 1)
            # Conflicting module name.
            self.assertRaises(ValueError, copyreg.add_extension,
                              mod[1:], func, code )
            self.assertRaises(ValueError, copyreg.remove_extension,
                              mod[1:], func, code )
            # Conflicting function name.
            self.assertRaises(ValueError, copyreg.add_extension,
                              mod, func[1:], code)
            self.assertRaises(ValueError, copyreg.remove_extension,
                              mod, func[1:], code)
            # Can't remove one that isn't registered at all.
            if code + 1 not in copyreg._inverted_registry:
                self.assertRaises(ValueError, copyreg.remove_extension,
                                  mod[1:], func[1:], code + 1)

        finally:
            e.restore()

        # Shouldn't be there anymore.
        self.assert_((mod, func) not in copyreg._extension_registry)
        # The code *may* be in copyreg._extension_registry, though, if
        # we happened to pick on a registered code.  So don't check for
        # that.

        # Check valid codes at the limits.
        for code in 1, 0x7fffffff:
            e = ExtensionSaver(code)
            try:
                copyreg.add_extension(mod, func, code)
                copyreg.remove_extension(mod, func, code)
            finally:
                e.restore()

        # Ensure invalid codes blow up.
        for code in -1, 0, 0x80000000:
            self.assertRaises(ValueError, copyreg.add_extension,
                              mod, func, code)

    def test_slotnames(self):
        self.assertEquals(copyreg._slotnames(WithoutSlots), [])
        self.assertEquals(copyreg._slotnames(WithWeakref), [])
        expected = ['_WithPrivate__spam']
        self.assertEquals(copyreg._slotnames(WithPrivate), expected)
        self.assertEquals(copyreg._slotnames(WithSingleString), ['spam'])
        expected = ['eggs', 'spam']
        expected.sort()
        result = copyreg._slotnames(WithInherited)
        result.sort()
        self.assertEquals(result, expected)


def test_main():
    support.run_unittest(CopyRegTestCase)


if __name__ == "__main__":
    test_main()
