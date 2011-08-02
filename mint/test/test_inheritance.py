import unittest

import mint


class DummyLoader(object):
    def __init__(self, templates):
        self.templates = templates
    def get_template(self, template_name):
        return self.templates[template_name]


class Inheritance(unittest.TestCase):

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


