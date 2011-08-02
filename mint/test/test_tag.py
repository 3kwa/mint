import unittest

import mint

class TagsAndText(unittest.TestCase):

    def test_empty(self):
        'Empty template'
        self.assertRaises(AssertionError, lambda: mint.Template(''))

    def test_empty2(self):
        'Not so empty template'
        self.assertEqual(mint.Template('\n').render(), '')

    def test_returns_markup(self):
        'Template.render() renturns Markup'
        self.assert_(isinstance(mint.Template('\n').render(), mint.Markup))

    def test_tag(self):
        'One tag'
        self.assertEqual(mint.Template('@tag').render(), '<tag></tag>')

    def test_tags(self):
        'Two tags'
        self.assertEqual(mint.Template('@tag\n'
                                       '@tag2').render(), '<tag></tag><tag2></tag2>')

    def test_nested_tags(self):
        'Nested tags'
        self.assertEqual(mint.Template('@tag\n'
                                       '    @tag2').render(), '<tag><tag2></tag2></tag>')

    def test_nested_tags2(self):
        'Nested tags more levels'
        self.assertEqual(mint.Template('@tag\n'
                                       '    @tag2\n'
                                       '        @tag3').render(),
                         '<tag><tag2><tag3></tag3></tag2></tag>')

    def test_nested_tags3(self):
        'Nested tags shortcuts'
        self.assertEqual(mint.Template('@tag @tag2 @tag3').render(),
                         '<tag><tag2><tag3></tag3></tag2></tag>')

    def test_nested_tags4(self):
        'Big question'
        #XXX: Throw SyntaxError wrong indent level
        self.assertEqual(mint.Template('@li @a.href(url) text\n'
                                       '    @p other text').render(),
                         '<li><a href="url">text\n</a><p>other text\n</p></li>')

    def test_text_content(self):
        'Tag with text content'
        self.assertEqual(mint.Template('@tag\n'
                                       '    text content').render(),
                         '<tag>text content\n</tag>')

    def test_text_content2(self):
        'Tag with text content shortcut'
        self.assertEqual(mint.Template('@tag text content').render(),
                         '<tag>text content\n</tag>')

    def test_text_content3(self):
        'Tag with multiline text content'
        self.assertEqual(mint.Template('@tag\n'
                                       '    text content\n'
                                       '    more text content here.').render(),
                         '<tag>text content\nmore text content here.\n</tag>')

    def test_mixed(self):
        'Mixed text and tags'
        self.assertEqual(mint.Template('text content\n'
                                       '@tag\n'
                                       'more text content here.').render(),
                         'text content\n<tag></tag>more text content here.\n')

    def test_mixed2(self):
        'Mixed text and tags with tags shortcuts'
        self.assertEqual(mint.Template('text content\n'
                                       '@tag inside tag\n'
                                       'more text content here.').render(),
                         'text content\n<tag>inside tag\n</tag>more text content here.\n')

    def test_mixed3(self):
        'Mixed text and tags with indention'
        self.assertEqual(mint.Template('text content\n'
                                       '@tag\n'
                                       '    inside tag\n'
                                       'more text content here.').render(),
                         'text content\n<tag>inside tag\n</tag>more text content here.\n')

    def test_tag_attr(self):
        'Tags attributes'
        self.assertEqual(mint.Template('@tag.attr(value)').render(),
                         '<tag attr="value"></tag>')

    def test_tag_attr2(self):
        'Tags attributes: values with spaces'
        self.assertEqual(mint.Template('@tag.attr( value )').render(),
                         '<tag attr=" value "></tag>')

    def test_tag_attr3(self):
        'Tags attributes: multiple attrs'
        self.assertEqual(mint.Template('@tag.attr(value).attr1(value1)').render(),
                         '<tag attr="value" attr1="value1"></tag>')

    def test_tag_attr4(self):
        'Tags attributes: more complex attribute names'
        self.assertEqual(mint.Template('@tag.ns:attr-name(value)').render(),
                                       '<tag ns:attr-name="value"></tag>')

    def test_tag_attr5(self):
        'Tags attributes: tags with content'
        self.assertEqual(mint.Template('@tag.ns:attr-name(value)\n'
                                       '    text content').render(),
                                       '<tag ns:attr-name="value">text content\n</tag>')

    def test_attr_assignment(self):
        'New attribute assignment'
        self.assertEqual(mint.Template('@tag\n'
                                       '    @.attr(value)').render(),
                                       '<tag attr="value"></tag>')

    def test_attr_assignment2(self):
        'New attribute assignment with default attribute value'
        self.assertEqual(mint.Template('@tag.attr(text)\n'
                                       '    @.attr(new value)').render(),
                                       '<tag attr="new value"></tag>')

    def test_attr_setting(self):
        'Attribute setter'
        self.assertEqual(mint.Template('@tag\n'
                                       '    @+attr(value)').render(),
                                       '<tag attr="value"></tag>')

    def test_attr_setting2(self):
        'Attribute setter with default attribute value'
        self.assertEqual(mint.Template('@tag.attr(value)\n'
                                       '    @+attr( value1)').render(),
                                       '<tag attr="value value1"></tag>')

    def test_mint_comment(self):
        'mint comments'
        self.assertEqual(mint.Template('// comment message').render(), '')

    def test_html_comment(self):
        'html comments'
        self.assertEqual(mint.Template('-- comment message').render(), '<!-- comment message -->')

    def test_html_comment2(self):
        'html comments with trail whitespaces'
        self.assertEqual(mint.Template('--  comment message  ').render(), '<!-- comment message -->')

    def test_backspace_escaping(self):
        'Backsapce escaping'
        self.assertEqual(mint.Template('\@tag.attr(value)').render(), '@tag.attr(value)\n')

    def test_escaping(self):
        'Text value escaping'
        self.assertEqual(mint.Template('text < > \' " &').render(),
                         'text &lt; &gt; &#39; &quot; &amp;\n')

    def test_escaping2(self):
        'Tag attr value escaping'
        self.assertEqual(mint.Template('@tag.attr(text < > \' " &)').render(),
                         '<tag attr="text &lt; &gt; &#39; &quot; &amp;"></tag>')

    def test_escaping3(self):
        'Markup object value'
        self.assertEqual(mint.Template('@tag\n'
                                       '    text <tag attr="&" />\n'
                                       '    {{ value }}').render(value=mint.Markup('<tag attr="&amp;" />')),
                         '<tag>text &lt;tag attr=&quot;&amp;&quot; /&gt;\n<tag attr="&amp;" />\n</tag>')

    def test_escaping4(self):
        'Markup object value in tag attr'
        self.assertEqual(mint.Template('@tag.attr({{ value }})').render(
                                value=mint.Markup('<tag attr="&amp;" />')),
                         '<tag attr="&lt;tag attr=&quot;&amp;&quot; /&gt;"></tag>')

    def test_spaces(self):
        'Whitespaces'
        self.assertRaises(SyntaxError, lambda: mint.Template('    \n'))

    def test_syntaxerror(self):
        'indented tag'
        self.assertRaises(SyntaxError, lambda: mint.Template('    \n'
                                                             '    @tag'))

    def test_syntaxerror2(self):
        'Nestead tags with no whitespace'
        self.assertRaises(mint.WrongToken, lambda: mint.Template('@tag@tag'))

    def test_syntaxerror3(self):
        'Nestead tag with text'
        self.assertEqual(mint.Template('@tag text @tag').render(), '<tag>text @tag\n</tag>')


