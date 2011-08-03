from markup import Markup
from looper import Looper

class Utils(object):

    class doctype:
        html_strict = Markup('<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.01//EN" '
                                '"http://www.w3.org/TR/html4/strict.dtd">')
        html_transitional = Markup('<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.01 '
                          'Transitional//EN" "http://www.w3.org/TR/html4/loose.dtd">')
        xhtml_strict = Markup('<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Strict//EN" '
                                 '"http://www.w3.org/TR/xhtml1/DTD/xhtml1-strict.dtd">')
        xhtml_transitional = Markup('<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 '
        'Transitional//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">')
        html5 = Markup('<!DOCTYPE html>')

    markup = Markup

    @staticmethod
    def loop(iterable):
        return Looper(iterable)

    @staticmethod
    def entity(char):
        return Markup(CHARS_ENTITIES.get(char, char))

    @staticmethod
    def script(src=None, data=None, type='text/javascript'):
        if src:
            return Markup('<script type="%s" src="%s"></script>' % (type, src))
        elif data:
            return Markup('<script type="%s">%s</script>' % (type, data))
        return ''

    @staticmethod
    def scripts(*args, **kwargs):
        result = []
        for name in args:
            result.append(utils.script(name, **kwargs))
        return ''.join(result)

    @staticmethod
    def link(href, rel='stylesheet', type='text/css'):
        return Markup('<link rel="%s" type="%s" href="%s" />' % (rel, type, href))



