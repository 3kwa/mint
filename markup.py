#NOTE: Taken from jinja2
class Markup(unicode):

    def __new__(cls, obj=u'', **kwargs):
        if hasattr(obj, '__html__'):
            obj = obj.__html__()
        return super(Markup, cls).__new__(cls, obj, **kwargs)

    def __html__(self):
        return self

    def __add__(self, other):
        if hasattr(other, '__html__') or isinstance(other, basestring):
            return self.__class__(unicode(self) + unicode(escape(other)))
        return NotImplemented

    def __radd__(self, other):
        if hasattr(other, '__html__') or isinstance(other, basestring):
            return self.__class__(unicode(escape(other)) + unicode(self))
        return NotImplemented

    def __mul__(self, num):
        if isinstance(num, (int, long)):
            return self.__class__(unicode.__mul__(self, num))
        return NotImplemented
    __rmul__ = __mul__

    def join(self, seq):
        return self.__class__(unicode.join(self, itertools.imap(escape, seq)))
    join.__doc__ = unicode.join.__doc__

    def split(self, *args, **kwargs):
        return map(self.__class__, unicode.split(self, *args, **kwargs))
    split.__doc__ = unicode.split.__doc__

    def rsplit(self, *args, **kwargs):
        return map(self.__class__, unicode.rsplit(self, *args, **kwargs))
    rsplit.__doc__ = unicode.rsplit.__doc__

    def splitlines(self, *args, **kwargs):
        return map(self.__class__, unicode.splitlines(self, *args, **kwargs))
    splitlines.__doc__ = unicode.splitlines.__doc__

    def __repr__(self):
        return 'Markup(%s)' % super(Markup, self).__repr__()


