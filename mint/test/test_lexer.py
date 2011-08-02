import unittest
from StringIO import StringIO

import mint

class Lexer(unittest.TestCase):

    def test_tokens(self):
        'Empty string'
        self.assertEqual(list(mint.tokenizer(StringIO())),
                         [(mint.TOKEN_EOF, 'EOF', 1, 0)])

    def test_tokens2(self):
        'Simple tokens'
        self.assertEqual(list(mint.tokenizer(StringIO('@@.@+()[]:;.,-+{{}}'))),
                         [(mint.TOKEN_TAG_START, '@', 1, 1),
                          (mint.TOKEN_TAG_ATTR_SET, '@.', 1, 2),
                          (mint.TOKEN_TAG_ATTR_APPEND, '@+', 1, 4),
                          (mint.TOKEN_PARENTHESES_OPEN, '(', 1, 6),
                          (mint.TOKEN_PARENTHESES_CLOSE, ')', 1, 7),
                          (mint.TOKEN_TEXT, '[]', 1, 8),
                          (mint.TOKEN_COLON, ':', 1, 10),
                          (mint.TOKEN_TEXT, ';', 1, 11),
                          (mint.TOKEN_DOT, '.', 1, 12),
                          (mint.TOKEN_TEXT, ',', 1, 13),
                          (mint.TOKEN_MINUS, '-', 1, 14),
                          (mint.TOKEN_PLUS, '+', 1, 15),
                          (mint.TOKEN_EXPRESSION_START, '{{', 1, 16),
                          (mint.TOKEN_EXPRESSION_END, '}}', 1, 18),
                          (mint.TOKEN_NEWLINE, '\n', 1, 20),
                          (mint.TOKEN_EOF, 'EOF', 2, 0)])

    def test_tokens3(self):
        'Special tokens'
        self.assertEqual(list(mint.tokenizer(StringIO('#base: #if #elif #else:#def #for #'))),
                         [(mint.TOKEN_BASE_TEMPLATE, '#base: ', 1, 1),
                          (mint.TOKEN_STATEMENT_IF, '#if ', 1, 8),
                          (mint.TOKEN_STATEMENT_ELIF, '#elif ', 1, 12),
                          (mint.TOKEN_STATEMENT_ELSE, '#else:', 1, 18),
                          (mint.TOKEN_SLOT_DEF, '#def ', 1, 24),
                          (mint.TOKEN_STATEMENT_FOR, '#for ', 1, 29),
                          (mint.TOKEN_STMT_CHAR, '#', 1, 34),
                          (mint.TOKEN_NEWLINE, '\n', 1, 35),
                          (mint.TOKEN_EOF, 'EOF', 2, 0)])

    def test_tokens4(self):
        'Two tokens in a row'
        self.assertEqual(list(mint.tokenizer(StringIO('{{{{#if #if '))),
                         [(mint.TOKEN_EXPRESSION_START, '{{', 1, 1),
                          (mint.TOKEN_EXPRESSION_START, '{{', 1, 3),
                          (mint.TOKEN_STATEMENT_IF, '#if ', 1, 5),
                          (mint.TOKEN_STATEMENT_IF, '#if ', 1, 9),
                          (mint.TOKEN_NEWLINE, '\n', 1, 13),
                          (mint.TOKEN_EOF, 'EOF', 2, 0)])

    def test_tokens5(self):
        'Special tokens (js)'
        self.assertEqual(list(mint.tokenizer(StringIO('#function #else if '))),
                         [(mint.TOKEN_SLOT_DEF, '#function ', 1, 1),
                          (mint.TOKEN_STATEMENT_ELIF, '#else if ', 1, 11),
                          (mint.TOKEN_NEWLINE, '\n', 1, 20),
                          (mint.TOKEN_EOF, 'EOF', 2, 0)])

    def test_tokens6(self):
        'expression shortcut token'
        self.assertEqual(list(mint.tokenizer(StringIO('@something= python_expression'))),
                         [(mint.TOKEN_TAG_START, u'@', 1, 1),
                         (mint.TOKEN_TEXT, u'something', 1, 2),
                         (mint.TOKEN_SHORT_EXPRESSION, u'=', 1, 11),
                         (mint.TOKEN_WHITESPACE, u' ', 1, 12),
                         (mint.TOKEN_TEXT, u'python_expression', 1, 13),
                         (mint.TOKEN_NEWLINE, '\n', 1, 30),
                         (mint.TOKEN_EOF, 'EOF', 2, 0)])

    def test_indent(self):
        'One indent'
        self.assertEqual(list(mint.tokenizer(StringIO('    '))),
                         [(mint.TOKEN_INDENT, '    ', 1, 1),
                          (mint.TOKEN_NEWLINE, '\n', 1, 5),
                          (mint.TOKEN_UNINDENT, '    ', 1, 5),
                          (mint.TOKEN_EOF, 'EOF', 2, 0)])

    def test_indent2(self):
        'One indent and new line'
        self.assertEqual(list(mint.tokenizer(StringIO('    \n'))),
                         [(mint.TOKEN_INDENT, '    ', 1, 1),
                          (mint.TOKEN_NEWLINE, '\n', 1, 5),
                          (mint.TOKEN_UNINDENT, '    ', 1, 5),
                          (mint.TOKEN_EOF, 'EOF', 2, 0)])

    def test_indent2_1(self):
        'Line and indent'
        self.assertEqual(list(mint.tokenizer(StringIO('\n'
                                                      '    '))),
                         [(mint.TOKEN_NEWLINE, '\n', 1, 1),
                          (mint.TOKEN_INDENT, '    ', 2, 1),
                          (mint.TOKEN_NEWLINE, '\n', 2, 5),
                          (mint.TOKEN_UNINDENT, '    ', 2, 5),
                          (mint.TOKEN_EOF, 'EOF', 3, 0)])

    def test_indent3(self):
        'Indent tokens'
        self.assertEqual(list(mint.tokenizer(StringIO('    \n'
                                                      '        \n'
                                                      '    '))),
                         [(mint.TOKEN_INDENT, '    ', 1, 1),
                          (mint.TOKEN_NEWLINE, '\n', 1, 5),
                          (mint.TOKEN_INDENT, '    ', 2, 5),
                          (mint.TOKEN_NEWLINE, '\n', 2, 9),
                          (mint.TOKEN_UNINDENT, '    ', 3, 1),
                          (mint.TOKEN_NEWLINE, '\n', 3, 5),
                          (mint.TOKEN_UNINDENT, '    ', 3, 5),
                          (mint.TOKEN_EOF, 'EOF', 4, 0)])

    def test_indent4(self):
        'Mixed indent'
        self.assertEqual(list(mint.tokenizer(StringIO('   \n'
                                                      '       '))),
                         [(mint.TOKEN_INDENT, '   ', 1, 1),
                          (mint.TOKEN_NEWLINE, '\n', 1, 4),
                          (mint.TOKEN_INDENT, '   ', 2, 4),
                          (mint.TOKEN_WHITESPACE, ' ', 2, 7),
                          (mint.TOKEN_NEWLINE, '\n', 2, 8),
                          (mint.TOKEN_UNINDENT, '   ', 2, 8),
                          (mint.TOKEN_UNINDENT, '   ', 2, 8),
                          (mint.TOKEN_EOF, 'EOF', 3, 0)])

    def test_indent5(self):
        'More mixed indent'
        self.assertEqual(list(mint.tokenizer(StringIO('    \n'
                                                      '   '))),
                         [(mint.TOKEN_INDENT, '    ', 1, 1),
                          (mint.TOKEN_NEWLINE, '\n', 1, 5),
                          (mint.TOKEN_UNINDENT, '    ', 1, 5),
                          (mint.TOKEN_WHITESPACE, '   ', 2, 1),
                          (mint.TOKEN_NEWLINE, '\n', 2, 4),
                          (mint.TOKEN_EOF, 'EOF', 3, 0)])

    def test_indent6(self):
        'Pyramid'
        self.assertEqual(list(mint.tokenizer(StringIO('\n'
                                                      '    \n'
                                                      '        \n'
                                                      '    '))),
                         [(mint.TOKEN_NEWLINE, '\n', 1, 1),
                          (mint.TOKEN_INDENT, '    ', 2, 1),
                          (mint.TOKEN_NEWLINE, '\n', 2, 5),
                          (mint.TOKEN_INDENT, '    ', 3, 5),
                          (mint.TOKEN_NEWLINE, '\n', 3, 9),
                          (mint.TOKEN_UNINDENT, '    ', 4, 1),
                          (mint.TOKEN_NEWLINE, '\n', 4, 5),
                          (mint.TOKEN_UNINDENT, '    ', 4, 5),
                          (mint.TOKEN_EOF, 'EOF', 5, 0)])

    def test_indent7(self):
        'Pyramid with double indent'
        self.assertEqual(list(mint.tokenizer(StringIO('\n'
                                                      '    \n'
                                                      '            \n'
                                                      '    '))),
                         [(mint.TOKEN_NEWLINE, '\n', 1, 1),
                          (mint.TOKEN_INDENT, '    ', 2, 1),
                          (mint.TOKEN_NEWLINE, '\n', 2, 5),
                          (mint.TOKEN_INDENT, '    ', 3, 5),
                          (mint.TOKEN_INDENT, '    ', 3, 9),
                          (mint.TOKEN_NEWLINE, '\n', 3, 13),
                          (mint.TOKEN_UNINDENT, '    ', 4, 1),
                          (mint.TOKEN_UNINDENT, '    ', 4, 1),
                          (mint.TOKEN_NEWLINE, '\n', 4, 5),
                          (mint.TOKEN_UNINDENT, '    ', 4, 5),
                          (mint.TOKEN_EOF, 'EOF', 5, 0)])


