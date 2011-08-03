import unittest

import mint

class IfTestCase(unittest.TestCase):

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


