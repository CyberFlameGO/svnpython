# Access WeakSet through the weakref module.
# This code is separated-out because it is needed
# by abc.py to load everything else at startup.

from _weakref import ref

__all__ = ['WeakSet']

class WeakSet:
    def __init__(self, data=None):
        self.data = set()
        def _remove(item, selfref=ref(self)):
            self = selfref()
            if self is not None:
                self.data.discard(item)
        self._remove = _remove
        if data is not None:
            self.update(data)

    def __iter__(self):
        for itemref in self.data:
            item = itemref()
            if item is not None:
                yield item

    def __len__(self):
        return sum(x() is not None for x in self.data)

    def __contains__(self, item):
        return ref(item) in self.data

    def __reduce__(self):
        return (self.__class__, (list(self),),
                getattr(self, '__dict__', None))

    def add(self, item):
        self.data.add(ref(item, self._remove))

    def clear(self):
        self.data.clear()

    def copy(self):
        return self.__class__(self)

    def pop(self):
        while True:
            try:
                itemref = self.data.pop()
            except KeyError:
                raise KeyError('pop from empty WeakSet')
            item = itemref()
            if item is not None:
                return item

    def remove(self, item):
        self.data.remove(ref(item))

    def discard(self, item):
        self.data.discard(ref(item))

    def update(self, other):
        if isinstance(other, self.__class__):
            self.data.update(other.data)
        else:
            for element in other:
                self.add(element)
    def __ior__(self, other):
        self.update(other)
        return self

    # Helper functions for simple delegating methods.
    def _apply(self, other, method):
        if not isinstance(other, self.__class__):
            other = self.__class__(other)
        newdata = method(other.data)
        newset = self.__class__()
        newset.data = newdata
        return newset

    def difference(self, other):
        return self._apply(other, self.data.difference)
    __sub__ = difference

    def difference_update(self, other):
        if self is other:
            self.data.clear()
        else:
            self.data.difference_update(ref(item) for item in other)
    def __isub__(self, other):
        if self is other:
            self.data.clear()
        else:
            self.data.difference_update(ref(item) for item in other)
        return self

    def intersection(self, other):
        return self._apply(other, self.data.intersection)
    __and__ = intersection

    def intersection_update(self, other):
        self.data.intersection_update(ref(item) for item in other)
    def __iand__(self, other):
        self.data.intersection_update(ref(item) for item in other)
        return self

    def issubset(self, other):
        return self.data.issubset(ref(item) for item in other)
    __lt__ = issubset

    def __le__(self, other):
        return self.data <= set(ref(item) for item in other)

    def issuperset(self, other):
        return self.data.issuperset(ref(item) for item in other)
    __gt__ = issuperset

    def __ge__(self, other):
        return self.data >= set(ref(item) for item in other)

    def __eq__(self, other):
        if not isinstance(other, self.__class__):
            return NotImplemented
        return self.data == set(ref(item) for item in other)

    def symmetric_difference(self, other):
        return self._apply(other, self.data.symmetric_difference)
    __xor__ = symmetric_difference

    def symmetric_difference_update(self, other):
        if self is other:
            self.data.clear()
        else:
            self.data.symmetric_difference_update(ref(item) for item in other)
    def __ixor__(self, other):
        if self is other:
            self.data.clear()
        else:
            self.data.symmetric_difference_update(ref(item) for item in other)
        return self

    def union(self, other):
        return self._apply(other, self.data.union)
    __or__ = union

    def isdisjoint(self, other):
        return len(self.intersection(other)) == 0
