import unittest

import mint

class For(unittest.TestCase):

    def test_for(self):
        'for statement'
        self.assertEqual(
            mint.Template('#for v in values:\n    {{ v }}').render(values=[1,2,3]),
            '1\n2\n3\n')
