import pickle
import unittest

from Controller import Controller
from Ranker import Ranker


class RankerTest(unittest.TestCase):
    def test_rank_query(self):
        c = Controller()
        dictionary = open("./test_data/test_dict.dic", "br")
        c.set_dictionary(pickle.load(dictionary))
        dictionary.close()
        cache = open("./test_data/test_cache.cch", "br")
        c.set_cache(pickle.load(cache))
        cache.close()
        d = c.get_dictionary()
        ranker = Ranker(d.term_dict, d.docs_dict, c.get_cache(), "./test_data/merged_terms_postings")

        result = set(ranker.rank_query(["development", 'innovating']))
        self.assertTrue("FBIS3-2811" in result)

        result = set(ranker.rank_query(["development"]))
        self.assertTrue("FBIS3-2811" not in result)


if __name__ == '__main__':
    unittest.main()
