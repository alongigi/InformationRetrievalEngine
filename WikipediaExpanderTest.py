import unittest

from WikipediaExpander import WikipediaExpander


class WikipediaExpanderTest(unittest.TestCase):
    def test_expand_query(self):

        query = "car"
        wx = WikipediaExpander()
        expended_query = wx.expand(query)
        self.assertGreaterEqual(len(expended_query), 2)


if __name__ == '__main__':
    unittest.main()
