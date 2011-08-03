import unittest
from StringIO import StringIO

from mint import get_mint_tree, tokenizer, \
    MintTemplate, TextNode, TagNode, TagAttrNode, ExpressionNode, \
    IfStmtNode, ElseStmtNode


class ParserTestCase(unittest.TestCase):

    def get_mint_tree(self, source):
        return get_mint_tree(tokenizer(StringIO(source)))

    def parsedEqual(self, string, tree):
      self.assertEqual(
          get_mint_tree(tokenizer(StringIO(string))),
          tree)


    def test_text_node(self):
        'Text node'
        self.parsedEqual(
            'text content',
            MintTemplate(body=[
                TextNode(
                    'text content\n',
                    lineno=1,
                    col_offset=1)
            ]))

    def test_short_expression_node(self):
        'Text node'
        self.parsedEqual(
            'text = content',
            MintTemplate(body=[
                TextNode(
                    'text = content\n',
                    lineno=1,
                    col_offset=1)
            ]))

    def test_short_expression_node_1(self):
        'Short expression is text node'
        self.parsedEqual(
            '@div = expression',
            MintTemplate(body=[
                TagNode(
                    u'div',
                    attrs=[],
                    body=[
                        TextNode(
                            u'= expression\n',
                            lineno=1,
                            col_offset=6)
                    ],
                    lineno=1,
                    col_offset=1)
            ]))

    def test_short_expression_node_2(self):
        'Short expression'
        self.parsedEqual(
            '@div= expression',
            MintTemplate(body=[
                TagNode(
                    u'div',
                    attrs=[],
                    body=[
                        ExpressionNode(
                            u'expression',
                            lineno=1,
                            col_offset=5)
                    ],
                    lineno=1,
                    col_offset=1)
            ]))

    def test_expression_node(self):
        'Expression node'
        #XXX: Do we really need TextNode with "\n" at the end?
        self.parsedEqual(
            '{{ expression }}',
            MintTemplate(body=[
                ExpressionNode(
                  'expression',
                  lineno=1,
                  col_offset=1),
                TextNode(
                    '\n',
                    lineno=1,
                    col_offset=17)
            ]))

    def test_expression_node2(self):
        'Expression node with text before'
        self.parsedEqual(
            'text value {{ expression }}',
            MintTemplate(body=[
                TextNode(
                    'text value ',
                    lineno=1,
                    col_offset=1),
                ExpressionNode(
                    'expression',
                    lineno=1,
                    col_offset=12),
                TextNode(
                    '\n',
                    lineno=1,
                    col_offset=28)
            ]))

    def test_expression_node3(self):
        'Expression node with text after'
        self.parsedEqual(\
            '{{ expression }} text value',
            MintTemplate(body=[
                ExpressionNode(
                    'expression',
                    lineno=1,
                    col_offset=1),
                TextNode(
                    ' text value\n',
                    lineno=1,
                    col_offset=17)
            ]))

    def test_tag_node(self):
        'Tag node'
        self.parsedEqual(
            '@tag',
            MintTemplate(body=[
                TagNode(
                    'tag',
                    lineno=1,
                    col_offset=1)
            ]))

    def test_tag_node2(self):
        'Tag node with attrs'
        self.parsedEqual(
            '@tag.attr(value)',
            MintTemplate(body=[
                TagNode(
                'tag',
                attrs=[
                    TagAttrNode(
                        'attr',
                        value=[
                            TextNode(
                                'value',
                                lineno=1,
                                col_offset=11
                        )],
                        lineno=1,
                        col_offset=6
                    )],
                    lineno=1,
                    col_offset=1)
            ]))

    def test_tag_node3(self):
        'Tag node with attrs and body text'
        self.parsedEqual(
            '@tag.attr(value)\n'
            '    text value',
            MintTemplate(body=[
                TagNode(
                    'tag',
                    attrs=[
                        TagAttrNode(
                            'attr',
                            value=[
                                  TextNode(
                                      'value',
                                      lineno=1,
                                      col_offset=11)
                              ],
                              lineno=1,
                              col_offset=6
                    )],
                    body=[
                        TextNode(
                            'text value\n',
                            lineno=2,
                            col_offset=5
                    )],
                    lineno=1,
                    col_offset=1)
            ]))

    def test_tag_node4(self):
        'Tag node with child tag'
        self.parsedEqual(
            '@tag\n'
            '    @tag2',
            MintTemplate(body=[
                TagNode(
                    'tag',
                    attrs=[],
                    body=[
                        TagNode(
                            'tag2',
                            attrs=[],
                            body=[],
                            lineno=2,
                            col_offset=5
                    )],
                    lineno=1,
                    col_offset=1
            )]))

    def test_tag_node5(self):
        'Nodes for short tags record'
        self.parsedEqual(
            '@tag @tag2',
            MintTemplate(body=[
                TagNode(
                    'tag',
                    attrs=[],
                    body=[
                        TagNode(
                            'tag2',
                            attrs=[],
                            body=[],
                            lineno=1,
                            col_offset=6
                    )],
                    lineno=1,
                    col_offset=1
            )]))

    def test_tag_node6(self):
        'Nodes for short tags record with text'
        self.parsedEqual(
            '@tag @tag2 text value',
            MintTemplate(body=[
                TagNode(
                    'tag',
                    attrs=[],
                    body=[
                        TagNode(
                            'tag2',
                            attrs=[],
                            body=[
                                TextNode(
                                    'text value\n',
                                    lineno=1,
                                    col_offset=12
                            )],
                            lineno=1,
                            col_offset=6
                    )],
                    lineno=1,
                    col_offset=1
            )]))

    def test_tag_attr(self):
        'Tag attribute node with expression'
        self.parsedEqual(
            '@tag.attr({{ expression }})',
            MintTemplate(body=[
                TagNode(
                    'tag',
                    attrs=[
                        TagAttrNode(
                            'attr',
                            value=[
                                ExpressionNode(
                                    'expression',
                                    lineno=1,
                                    col_offset=11
                            )],
                            lineno=1,
                            col_offset=6
                    )],
                    lineno=1,
                    col_offset=1
            )]))

    def test_if_node(self):
        'If statement'
        self.parsedEqual(
            '#if statement',
            MintTemplate(body=[
                IfStmtNode(
                    '#if statement',
                    body=[],
                    lineno=1,
                    col_offset=1
            )]))

    def test_if_node2(self):
        'If statement with body'
        self.parsedEqual(
            '#if statement\n'
            '    text value',
            MintTemplate(body=[
                IfStmtNode(
                    '#if statement',
                    body=[
                        TextNode(
                            'text value\n',
                            lineno=2,
                            col_offset=5
                    )],
                    lineno=1,
                    col_offset=1
            )]))

    def test_if_node3(self):
        'If statement with else'
        self.parsedEqual(
            '#if statement\n'
            '    text value\n'
            '#else:\n'
            '    another text value',
            MintTemplate(body=[
                IfStmtNode(
                    '#if statement',
                    body=[
                        TextNode(
                            'text value\n',
                            lineno=2,
                            col_offset=5
                    )],
                    orelse=[
                        ElseStmtNode(
                        body=[
                            TextNode(
                                'another text value\n',
                                lineno=4,
                                col_offset=5
                        )],
                        lineno=3,
                        col_offset=1
                    )],
                    lineno=1,
                    col_offset=1
            )]))
