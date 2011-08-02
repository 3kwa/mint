import unittest

import mint

class PprintTests(unittest.TestCase):

    def test_empty(self):
        'Pprint not so empty template'
        self.assertEqual(
            mint.Template('\n', pprint=True).render(),
            '')

    def test_tag(self):
        'Pprint tag'
        self.assertEqual(
            mint.Template('@tag', pprint=True).render(),
            '<tag></tag>\n')

    def test_tags(self):
        'Pprint tags'
        self.assertEqual(
            mint.Template('@tag @tag', pprint=True).render(),
             '<tag>\n'
             '  <tag></tag>\n'
             '</tag>\n')

    def test_tags2(self):
        'Pprint tags in a row'
        self.assertEqual(
            mint.Template('@tag\n'
                          '@tag', pprint=True).render(),
            '<tag></tag>\n'
            '<tag></tag>\n')

    def test_tag_attrs(self):
        'Pprint tag with attrs'
        self.assertEqual(
            mint.Template('@tag.attr(value)', pprint=True).render(),
            '<tag attr="value"></tag>\n')

    def test_tags_attrs(self):
        'Pprint tags with attrs'
        self.assertEqual(
            mint.Template('@tag.attr(value) @tag.attr(value)', pprint=True).render(),
             '<tag attr="value">\n'
             '  <tag attr="value"></tag>\n'
             '</tag>\n')

    def test_tag_text(self):
        'Pprint tag with text content'
        self.assertEqual(
            mint.Template('@tag text text', pprint=True).render(),
            '<tag>\n'
            '  text text\n'
            '</tag>\n')

    def test_tag_big_text(self):
        'Pprint tag with big text content'
        self.assertEqual(mint.Template('@tag Lorem ipsum dolor sit amet, consectetuer adipiscing elit, sed diam nonummy nibh euismod tincidunt ut laoreet dolore magna aliquam erat volutpat. Ut wisi enim ad minim veniam, quis nostrud exerci tation ullamcorper suscipit lobortis nisl ut aliquip ex ea commodo consequat.', pprint=True).render(),
                        '<tag>\n'
                        '  Lorem ipsum dolor sit amet, consectetuer adipiscing elit, sed diam nonummy nibh euismod tincidunt ut laoreet dolore magna aliquam erat volutpat. Ut wisi enim ad minim veniam, quis nostrud exerci tation ullamcorper suscipit lobortis nisl ut aliquip ex ea commodo consequat.\n'
                        '</tag>\n')

    def test_slot(self):
        'Pprint tag with slot'
        self.assertEqual(mint.Template('#def slot():\n'
                                       '  @tag.attr(value)\n'
                                       '@tag\n'
                                       '  #slot()', pprint=True).render(),
                         '<tag>\n'
                         '  <tag attr="value"></tag>\n'
                         '</tag>\n')

    def test_slot_tags(self):
        'Pprint tag with slot with tags'
        self.assertEqual(mint.Template('#def slot():\n'
                                       '  @tag\n'
                                       '    @tag.attr(value) text\n'
                                       '@tag\n'
                                       '  #slot()', pprint=True).render(),
                         '<tag>\n'
                         '  <tag>\n'
                         '    <tag attr="value">\n'
                         '      text\n'
                         '    </tag>\n'
                         '  </tag>\n'
                         '</tag>\n')



