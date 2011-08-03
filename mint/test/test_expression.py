import unittest

import mint

class ExpressionTestCase(unittest.TestCase):

    def renderTemplateIs(self, template, string):
        self.assertEqual(
          mint.Template(template).render(),
          string)

    def test_expression(self):
        'Python expression'
        self.renderTemplateIs(
            '{{ "Hello, mint!" }}',
            'Hello, mint!\n')

    def test_expression1(self):
        'Wrong Python expression'
        self.assertRaises(
            SyntaxError,
            lambda: mint.Template('{{ "Hello, mint! }}').render())

    def test_expression_and_text(self):
        'Python expression and text after'
        self.renderTemplateIs(
            '{{ "Hello," }} mint!',
            'Hello, mint!\n')

    def test_expressoin_and_text2(self):
        'Python expression and text before'
        self.renderTemplateIs(
            'Hello, {{ "mint!" }}',
            'Hello, mint!\n')

    def test_expressoin_and_text3(self):
        'Python expression and text at new line'
        self.renderTemplateIs(
            '{{ "Hello," }}\nmint!',
            'Hello,\nmint!\n')

    def test_short_expression1(self):
        'Python expression @tag='
        self.renderTemplateIs(
            '@div= 1+1',
            '<div>2</div>')

    def test_short_expression1(self):
        'not a Python expression @tag ='
        self.renderTemplateIs(
            '@div = 1+1',
            '<div>= 1+1\n</div>')
