# -*- coding: utf-8 -*-

import os
import glob
import unittest
import types
from StringIO import StringIO

import mint



class DummyLoader(object):
    def __init__(self, templates):
        self.templates = templates
    def get_template(self, template_name):
        return self.templates[template_name]


class PythonPart(unittest.TestCase):

    def test_expression(self):
        'Python expression'
        self.assertEqual(mint.Template('{{ "Hello, mint!" }}').render(), 'Hello, mint!\n')

    def test_expression1(self):
        'Wrong Python expression'
        self.assertRaises(SyntaxError, lambda: mint.Template('{{ "Hello, mint! }}').render())

    def test_expressoin_and_text(self):
        'Python expression and text after'
        self.assertEqual(mint.Template('{{ "Hello," }} mint!').render(), 'Hello, mint!\n')

    def test_expressoin_and_text2(self):
        'Python expression and text before'
        self.assertEqual(mint.Template('Hello, {{ "mint!" }}').render(), 'Hello, mint!\n')

    def test_expressoin_and_text3(self):
        'Python expression and text at new line'
        self.assertEqual(mint.Template('{{ "Hello," }}\n'
                                       'mint!').render(), 'Hello,\nmint!\n')

    def test_if(self):
        'if statement (true)'
        self.assertEqual(mint.Template('#if True:\n'
                                       '    true').render(), 'true\n')

    def test_if1(self):
        'if statement (false)'
        self.assertEqual(mint.Template('#if False:\n'
                                       '    true\n'
                                       'false').render(), 'false\n')

    def test_if2(self):
        'if-else statements'
        self.assertEqual(mint.Template('#if False:\n'
                                       '    true\n'
                                       '#else:\n'
                                       '    false').render(), 'false\n')

    def test_if3(self):
        'if-elif-else statements'
        self.assertEqual(mint.Template('#if False:\n'
                                       '    if\n'
                                       '#elif True:\n'
                                       '    elif\n'
                                       '#else:\n'
                                       '    else').render(), 'elif\n')

    def test_if4(self):
        'if-elif-else statements and nested statements'
        self.assertEqual(mint.Template('#if False:\n'
                                       '    if\n'
                                       '#elif True:\n'
                                       '    elif\n'
                                       '    #if False:\n'
                                       '        nested if\n'
                                       '    #else:\n'
                                       '        nested else\n'
                                       '#else:\n'
                                       '    else').render(), 'elif\nnested else\n')

    def test_for(self):
        'for statement'
        self.assertEqual(mint.Template('#for v in values:\n'
                                       '    {{ v }}').render(values=[1,2,3]), '1\n2\n3\n')

    def test_slotdef(self):
        'Slot definition'
        self.assertEqual(mint.Template('#def count():\n'
                                       '    {{ value }}').render(value=1), '')

    def test_slotcall(self):
        'Slot call'
        self.assertEqual(mint.Template('#def count():\n'
                                       '    {{ value }}\n'
                                       '#count()').render(value=1), '1\n')

    def test_slotcall_from_python(self):
        'Slot call from python code'
        t = mint.Template('#def count(value):\n'
                          '    {{ value }}\n'
                          '#count()')
        slot = t.slot('count')
        self.assert_(isinstance(slot, types.FunctionType))
        self.assertEqual(slot(1), '1\n')

    def test_inheritance(self):
        'One level inheritance'
        loader = DummyLoader({
            'base.mint':mint.Template('#def slot():\n'
                                      '    base slot\n'
                                      '#slot()'),
        })
        self.assertEqual(mint.Template('#base: base.mint\n'
                                       '#def slot():\n'
                                       '    overrided slot\n', loader=loader).render(),
                        'overrided slot\n')

    def test_inheritance2(self):
        'One level inheritance with different slots'
        loader = DummyLoader({
            'base.mint':mint.Template('#def slot1():\n'
                                      '    base slot\n'
                                      '#slot1()\n'
                                      '#slot2()'),
        })
        self.assertEqual(mint.Template('#base: base.mint\n'
                                       '#def slot2():\n'
                                       '    overrided slot\n', loader=loader).render(),
                        'base slot\noverrided slot\n')

    def test_inheritance3(self):
        'Two level inheritance'
        loader = DummyLoader({
            'base.mint':mint.Template('#def slot():\n'
                                      '    base slot\n'
                                      '#slot()'),
        })
        loader.templates.update({
            'base2.mint':mint.Template('#base: base.mint\n'
                                       '#def slot():\n'
                                       '    base2 slot\n', loader=loader),
        })
        self.assertEqual(mint.Template('#base: base2.mint\n'
                                       '#def slot():\n'
                                       '    overrided slot\n', loader=loader).render(),
                        'overrided slot\n')

    def test_inheritance4(self):
        'Two level inheritance and slots on differrent levels'
        loader = DummyLoader({
            'base.mint':mint.Template('#def slot1():\n'
                                      '    base slot\n'
                                      '#slot1()\n'
                                      '#slot2()\n'
                                      '#slot3()\n'),
        })
        loader.templates.update({
            'base2.mint':mint.Template('#base: base.mint\n'
                                       '#def slot2():\n'
                                       '    base2 slot\n', loader=loader),
        })
        self.assertEqual(mint.Template('#base: base2.mint\n'
                                       '#def slot3():\n'
                                       '    overrided slot\n', loader=loader).render(),
                        'base slot\nbase2 slot\noverrided slot\n')

    def test_inheritance5(self):
        'Two level inheritance and slots on differrent levels 2'
        loader = DummyLoader({
            'base.mint':mint.Template('#def slot1():\n'
                                      '    base slot\n'
                                      '#slot1()\n'
                                      '#slot2()\n'
                                      '#slot3()\n'),
        })
        loader.templates.update({
            'base2.mint':mint.Template('#base: base.mint\n'
                                       '#def slot2():\n'
                                       '    base2 slot\n', loader=loader),
        })
        self.assertEqual(mint.Template('#base: base2.mint\n'
                                       '#def slot2():\n'
                                       '    overrided base2 slot\n'
                                       '#def slot3():\n'
                                       '    overrided slot\n', loader=loader).render(),
                        'base slot\noverrided base2 slot\noverrided slot\n')

    def test_inheritance6(self):
        'Two level inheritance and __base__'
        loader = DummyLoader({
            'base.mint':mint.Template('#def slot():\n'
                                      '    base slot\n'
                                      '#slot()'),
        })
        loader.templates.update({
            'base2.mint':mint.Template('#base: base.mint\n'
                                       '#def slot():\n'
                                       '    {{ __base__() }}\n'
                                       '    base2 slot\n', loader=loader),
        })
        self.assertEqual(mint.Template('#base: base2.mint\n'
                                       '#def slot():\n'
                                       '    {{ __base__() }}\n'
                                       '    overrided slot\n', loader=loader).render(),
                        'base slot\n\nbase2 slot\n\noverrided slot\n')


class PprintTests(unittest.TestCase):

    def test_empty(self):
        'Pprint not so empty template'
        self.assertEqual(mint.Template('\n', pprint=True).render(), '')

    def test_tag(self):
        'Pprint tag'
        self.assertEqual(mint.Template('@tag', pprint=True).render(), '<tag></tag>\n')

    def test_tags(self):
        'Pprint tags'
        self.assertEqual(mint.Template('@tag @tag', pprint=True).render(),
                         '<tag>\n'
                         '  <tag></tag>\n'
                         '</tag>\n')

    def test_tags2(self):
        'Pprint tags in a row'
        self.assertEqual(mint.Template('@tag\n'
                                       '@tag', pprint=True).render(),
                         '<tag></tag>\n'
                         '<tag></tag>\n')

    def test_tag_attrs(self):
        'Pprint tag with attrs'
        self.assertEqual(mint.Template('@tag.attr(value)', pprint=True).render(), '<tag attr="value"></tag>\n')

    def test_tags_attrs(self):
        'Pprint tags with attrs'
        self.assertEqual(mint.Template('@tag.attr(value) @tag.attr(value)', pprint=True).render(),
                         '<tag attr="value">\n'
                         '  <tag attr="value"></tag>\n'
                         '</tag>\n')

    def test_tag_text(self):
        'Pprint tag with text content'
        self.assertEqual(mint.Template('@tag text text', pprint=True).render(),
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



