import unittest
import types

import mint

class Slot(unittest.TestCase):

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


