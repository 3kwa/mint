class Looper:
    'Cool class taken from PPA project'
    class _Item:
        def __init__(self, index, has_next):
            self.index = index
            self.has_next = has_next
            self.last = not has_next
            self.first = not index
        @property
        def odd(self):
            return self.index % 2
        @property
        def even(self):
            return not self.index % 2
        def cycle(self, *args):
            'Magic method (adopted ;)'
            return args[self.index % len(args)]

    def __init__(self, iterable):
        self._iterator = iter(iterable)

    def _shift(self):
        try:
            self._next = self._iterator.next()
        except StopIteration:
            self._has_next = False
        else:
            self._has_next = True

    def __iter__(self):
        self._shift()
        index = 0
        while self._has_next:
            value = self._next
            self._shift()
            yield value, self._Item(index, self._has_next)
            index += 1


