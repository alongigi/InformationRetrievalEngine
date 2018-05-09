import pickle
import unittest

from Controller import Controller
from Searcher import Searcher


class ParserTest(unittest.TestCase):

    def test_search_query(self):
        c = Controller()
        dictionary = open("./test_data/test_dict.dic", "br")
        c.set_dictionary(pickle.load(dictionary))
        dictionary.close()
        cache = open("./test_data/test_cache.cch", "br")
        c.set_cache(pickle.load(cache))
        cache.close()
        d = c.get_dictionary()
        searcher = Searcher("./test_data/stop_words.txt", d.term_dict, d.docs_dict, c.get_cache(), "./test_data/merged_terms_postings")

        result = set(searcher.search_query("innovating"))
        self.assertTrue("FBIS3-2811" in result)

        result = set(searcher.search_query("development"))
        self.assertTrue("FBIS3-2811" not in result)

        result = set(searcher.search_query("supervision"))
        self.assertTrue("FBIS3-50" in result)

        result = set(searcher.search_query("innovating development television"))
        self.assertTrue("FT942-13571" not in result)

        result = set(searcher.search_query("New York, Massachusetts, California and Washington"))
        self.assertTrue("LA010790-0030" not in result)


if __name__ == '__main__':
    unittest.main()
