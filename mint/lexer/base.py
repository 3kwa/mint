import re

class WrongToken(Exception): pass

class BaseToken(object):
    pass

class TokenWrapper(BaseToken):
    '''
    Objects of this class reprezents tokens
    '''

    def __init__(self, token, value=None, regex_str=None):
        assert value or regex_str, 'Provide token text value or regex'
        self.token = intern(token)
        if regex_str is not None:
            self.regex = re.compile(regex_str, re.U)
        else:
            self.regex = re.compile(r'%s' % re.escape(value), re.U)

    def __str__(self):
        return self.token

    __repr__ = __str__


class TextToken(BaseToken):
    'Special token for text'
    def __str__(self):
        return 'text'
    __repr__ = __str__


class TokenIndent(BaseToken):
    def __str__(self):
        return 'indent'
    __repr__ = __str__


class TokenUnindent(BaseToken):
    def __str__(self):
        return 'unindent'
    __repr__ = __str__


class EOF(BaseToken):
    'Special token'
    def __str__(self):
        return 'eof'
    __repr__ = __str__

