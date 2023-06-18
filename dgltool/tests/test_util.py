import tomlkit
from .. import util
import unittest


class TestAllAliases(unittest.TestCase):
    def test_empty(self):
        cfg = tomlkit.loads('')
        self.assertEqual([], list(util.all_aliases(cfg)))

    def test_multiple(self):
        cfg = tomlkit.loads(
            """
[[account]]
aliases = ["abc", "def"]

[[account]]
aliases = ["ghj"]
"""
        )
        self.assertEqual(['abc', 'def', 'ghj'], list(util.all_aliases(cfg)))
