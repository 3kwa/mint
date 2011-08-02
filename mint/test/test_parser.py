import unittest
from StringIO import StringIO

import mint

class Parser(unittest.TestCase):

    def get_mint_tree(self, source):
        return mint.get_mint_tree(mint.tokenizer(StringIO(source)))

    def test_text_node(self):
        'Text node'
        tree = self.get_mint_tree('text content')
        self.assertEqual(tree,
                         mint.MintTemplate(body=[
                             mint.TextNode('text content\n', lineno=1, col_offset=1)]))

    def test_short_expression_node(self):
        'Text node'
        tree = self.get_mint_tree('text = content')
        self.assertEqual(tree,
                         mint.MintTemplate(body=[
                             mint.TextNode('text = content\n', lineno=1, col_offset=1)]))

    def test_short_expression_node_1(self):
        'Short expression is text node'
        tree = self.get_mint_tree('@div = expression')
        self.assertEqual(tree,
            mint.MintTemplate(
                body=[mint.TagNode(u'div', attrs=[], body=[
                  mint.TextNode(u'= expression\n', lineno=1, col_offset=6)],
                  lineno=1, col_offset=1)]))

    def test_short_expression_node_2(self):
        'Short expression'
        tree = self.get_mint_tree('@div= expression')
        self.assertEqual(tree,
            mint.MintTemplate(
                body=[mint.TagNode(u'div', attrs=[], body=[
                  mint.ExpressionNode(u'expression', lineno=1, col_offset=5)
                  #,mint.TextNode(u'\n', lineno=1, col_offset=1)
                  ],
                  lineno=1, col_offset=1)]))

    def test_expression_node(self):
        'Expression node'
        tree = self.get_mint_tree('{{ expression }}')
        #XXX: Do we really need TextNode with "\n" at the end?
        self.assertEqual(tree,
                         mint.MintTemplate(body=[
                             mint.ExpressionNode('expression', lineno=1, col_offset=1),
                             mint.TextNode('\n', lineno=1, col_offset=17)]))

    def test_expression_node2(self):
        'Expression node with text before'
        tree = self.get_mint_tree('text value {{ expression }}')
        self.assertEqual(tree,
                         mint.MintTemplate(body=[
                             mint.TextNode('text value ', lineno=1, col_offset=1),
                             mint.ExpressionNode('expression', lineno=1, col_offset=12),
                             mint.TextNode('\n', lineno=1, col_offset=28)]))

    def test_expression_node3(self):
        'Expression node with text after'
        tree = self.get_mint_tree('{{ expression }} text value')
        self.assertEqual(tree,
                         mint.MintTemplate(body=[
                             mint.ExpressionNode('expression', lineno=1, col_offset=1),
                             mint.TextNode(' text value\n', lineno=1, col_offset=17)]))

    def test_tag_node(self):
        'Tag node'
        tree = self.get_mint_tree('@tag')
        self.assertEqual(tree,
                         mint.MintTemplate(body=[
                            mint.TagNode('tag', lineno=1, col_offset=1)]))

    def test_tag_node2(self):
        'Tag node with attrs'
        tree = self.get_mint_tree('@tag.attr(value)')
        self.assertEqual(tree,
                         mint.MintTemplate(body=[
                             mint.TagNode('tag',
                                           attrs=[mint.TagAttrNode('attr',
                                                                   value=[mint.TextNode('value',
                                                                                        lineno=1,
                                                                                        col_offset=11)],
                                                                    lineno=1, col_offset=6)],
                                           lineno=1, col_offset=1)]))

    def test_tag_node3(self):
        'Tag node with attrs and body text'
        tree = self.get_mint_tree('@tag.attr(value)\n'
                                  '    text value')
        self.assertEqual(tree,
                         mint.MintTemplate(body=[
                             mint.TagNode('tag',
                                           attrs=[mint.TagAttrNode('attr',
                                                                   value=[mint.TextNode('value',
                                                                                        lineno=1,
                                                                                        col_offset=11)],
                                                                    lineno=1, col_offset=6)],
                                           body=[mint.TextNode('text value\n', lineno=2, col_offset=5)],
                                           lineno=1, col_offset=1)]))

    def test_tag_node4(self):
        'Tag node with child tag'
        tree = self.get_mint_tree('@tag\n'
                                  '    @tag2')
        self.assertEqual(tree,
                         mint.MintTemplate(body=[
                             mint.TagNode('tag', attrs=[],
                                           body=[mint.TagNode('tag2', attrs=[], body=[],
                                                              lineno=2, col_offset=5)],
                                           lineno=1, col_offset=1)]))

    def test_tag_node5(self):
        'Nodes for short tags record'
        tree = self.get_mint_tree('@tag @tag2')
        self.assertEqual(tree,
                         mint.MintTemplate(body=[
                             mint.TagNode('tag', attrs=[],
                                           body=[mint.TagNode('tag2', attrs=[], body=[],
                                                              lineno=1, col_offset=6)],
                                           lineno=1, col_offset=1)]))

    def test_tag_node6(self):
        'Nodes for short tags record with text'
        tree = self.get_mint_tree('@tag @tag2 text value')
        self.assertEqual(tree,
                         mint.MintTemplate(body=[
                             mint.TagNode('tag', attrs=[],
                                           body=[mint.TagNode('tag2', attrs=[],
                                                              body=[mint.TextNode('text value\n',
                                                                                  lineno=1, col_offset=12)],
                                                              lineno=1, col_offset=6)],
                                           lineno=1, col_offset=1)]))

    def test_tag_attr(self):
        'Tag attribute node with expression'
        tree = self.get_mint_tree('@tag.attr({{ expression }})')
        self.assertEqual(tree,
                         mint.MintTemplate(body=[
                             mint.TagNode('tag',
                                           attrs=[mint.TagAttrNode('attr',
                                                                   value=[mint.ExpressionNode('expression',
                                                                                              lineno=1,
                                                                                              col_offset=11)],
                                                                   lineno=1, col_offset=6)],
                                           lineno=1, col_offset=1)]))

    def test_if_node(self):
        'If statement'
        tree = self.get_mint_tree('#if statement')
        self.assertEqual(tree,
                         mint.MintTemplate(body=[
                             mint.IfStmtNode('#if statement', body=[], lineno=1, col_offset=1)]))

    def test_if_node2(self):
        'If statement with body'
        tree = self.get_mint_tree('#if statement\n'
                                  '    text value')
        self.assertEqual(tree,
                         mint.MintTemplate(body=[
                             mint.IfStmtNode('#if statement',
                                             body=[mint.TextNode('text value\n', lineno=2, col_offset=5)],
                                             lineno=1, col_offset=1)]))

    def test_if_node3(self):
        'If statement with else'
        tree = self.get_mint_tree('#if statement\n'
                                  '    text value\n'
                                  '#else:\n'
                                  '    another text value')
        self.assertEqual(tree,
                         mint.MintTemplate(body=[
                             mint.IfStmtNode('#if statement',
                                             body=[mint.TextNode('text value\n', lineno=2, col_offset=5)],
                                             orelse=[mint.ElseStmtNode(body=[
                                                 mint.TextNode('another text value\n',
                                                               lineno=4, col_offset=5)],
                                                                       lineno=3, col_offset=1)],
                                             lineno=1, col_offset=1)]))


