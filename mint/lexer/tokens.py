import re

from __init__ import EOF, TokenUnindent, TokenIndent, TextToken, TokenWrapper
#from base import EOF, TokenUnindent, TokenIndent, TextToken, TokenWrapper

# constants
TAG_CHAR = '@'
STMT_CHAR = '#'
COMMENT_CHAR = '--'

# Tokens
TOKEN_TAG_START = TokenWrapper(
    'tag_start',
    value=TAG_CHAR)

TOKEN_TAG_ATTR_SET = TokenWrapper(
    'tag_attr_set',
    value='%s.' % TAG_CHAR)

TOKEN_TAG_ATTR_APPEND = TokenWrapper(
    'tag_attr_append',
    value='%s+' % TAG_CHAR)

TOKEN_BASE_TEMPLATE = TokenWrapper(
    'base_template',
    value='%sbase: ' % STMT_CHAR)

TOKEN_STATEMENT_IF = TokenWrapper(
    'statement_if',
    value='%sif ' % STMT_CHAR)

TOKEN_STATEMENT_ELIF = TokenWrapper(
    'statement_elif',
    regex_str=r'(%selif |%selse if )' % (
        re.escape(STMT_CHAR),
        re.escape(STMT_CHAR)))

TOKEN_STATEMENT_ELSE = TokenWrapper(
    'statement_else',
    value='%selse:' % STMT_CHAR)

TOKEN_STATEMENT_FOR = TokenWrapper(
    'statement_for',
    value='%sfor ' % STMT_CHAR)

TOKEN_SLOT_DEF = TokenWrapper(
    'slot_def',
    regex_str=r'(%sdef |%sfunction )' % (
        re.escape(STMT_CHAR),
        re.escape(STMT_CHAR)))

TOKEN_STMT_CHAR = TokenWrapper(
    'hash',
    value=STMT_CHAR)

TOKEN_COMMENT = TokenWrapper(
    'comment',
    value=COMMENT_CHAR)

TOKEN_BACKSLASH = TokenWrapper(
    'backslash',
    value='\\')

TOKEN_DOT = TokenWrapper(
    'dot',
    value='.')

TOKEN_PLUS = TokenWrapper(
    'plus',
    value='+')

TOKEN_MINUS = TokenWrapper(
    'minus',
    value='-')

TOKEN_COLON = TokenWrapper(
    'colon',
    value=':')

TOKEN_PARENTHESES_OPEN = TokenWrapper(
    'parentheses_open',
    value='(')

TOKEN_PARENTHESES_CLOSE = TokenWrapper(
    'parentheses_close',
    value=')')

TOKEN_EXPRESSION_START = TokenWrapper(
    'expression_start',
    value='{{')

TOKEN_EXPRESSION_END = TokenWrapper(
    'expression_end',
    value='}}')

TOKEN_WHITESPACE = TokenWrapper(
    'whitespace',
    regex_str=r'\s+')

TOKEN_NEWLINE = TokenWrapper(
    'newline',
    regex_str=r'(\r\n|\r|\n)')

TOKEN_SHORT_EXPRESSION = TokenWrapper(
    'short_expression',
    regex_str='=')

TOKEN_EOF = EOF()
TOKEN_TEXT = TextToken()
TOKEN_INDENT = TokenIndent()
TOKEN_UNINDENT = TokenUnindent()



tokens = (
    TOKEN_TAG_ATTR_SET,
    TOKEN_TAG_ATTR_APPEND,
    TOKEN_TAG_START,
    TOKEN_BASE_TEMPLATE,
    TOKEN_STATEMENT_IF,
    TOKEN_STATEMENT_ELIF,
    TOKEN_STATEMENT_ELSE,
    TOKEN_STATEMENT_FOR,
    TOKEN_SLOT_DEF,
    TOKEN_STMT_CHAR,
    TOKEN_COMMENT,
    TOKEN_BACKSLASH,
    TOKEN_DOT,
    TOKEN_PLUS,
    TOKEN_MINUS,
    TOKEN_PARENTHESES_OPEN,
    TOKEN_PARENTHESES_CLOSE,
    TOKEN_EXPRESSION_START,
    TOKEN_EXPRESSION_END,
    TOKEN_COLON,
    TOKEN_WHITESPACE,
    TOKEN_NEWLINE,
    TOKEN_SHORT_EXPRESSION,
)

all_tokens = list(tokens) + [TOKEN_EOF, TOKEN_TEXT, TOKEN_INDENT, TOKEN_UNINDENT]
all_except = lambda *t: filter(lambda x: x not in t, all_tokens)
re_comment = re.compile(r'\s*//')

