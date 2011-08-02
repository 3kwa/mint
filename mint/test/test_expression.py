import unittest

import mint

class Expression(unittest.TestCase):

    def test_expression(self):
        'Python expression'
        self.assertEqual(
            mint.Template('{{ "Hello, mint!" }}').render(),
            'Hello, mint!\n')

    def test_expression1(self):
        'Wrong Python expression'
        self.assertRaises(
            SyntaxError,
            lambda: mint.Template('{{ "Hello, mint! }}').render())

    def test_expressoin_and_text(self):
        'Python expression and text after'
        self.assertEqual(
            mint.Template('{{ "Hello," }} mint!').render(),
            'Hello, mint!\n')

    def test_expressoin_and_text2(self):
        'Python expression and text before'
        self.assertEqual(
            mint.Template('Hello, {{ "mint!" }}').render(),
            'Hello, mint!\n')

    def test_expressoin_and_text3(self):
        'Python expression and text at new line'
        self.assertEqual(
            mint.Template('{{ "Hello," }}\nmint!').render(),
            'Hello,\nmint!\n')

    def test_short_expression1(self):
        'Python expression @tag='
        self.assertEqual(
            mint.Template('@div= 1+1').render(),
            '<div>2</div>')

    def test_short_expression1(self):
        'not a Python expression @tag ='
        self.assertEqual(
            mint.Template('@div = 1+1').render(),
            '<div>= 1+1\n</div>')
