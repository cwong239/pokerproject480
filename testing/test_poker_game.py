import sys, os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'pokerGame')))

import unittest
print(sys.path)
from poker import Game # type: ignore

class TestPoker(unittest.TestCase):

    def test_upper(self):
        g = Game(1)
        assert g

if __name__ == '__main__':
    unittest.main()