import pickle
import unittest

from Controller import Controller
from Document import Document
from ReadFile import ReadFile
from Summerizer import Summerizer


class SummarizerTest(unittest.TestCase):
    def test_something(self):
        c = Controller()
        dictionary = open("./test_data/test_dict.dic", "br")
        c.set_dictionary(pickle.load(dictionary))
        dictionary.close()
        cache = open("./test_data/test_cache.cch", "br")
        c.set_cache(pickle.load(cache))
        cache.close()
        dicts = c.get_dictionary()
        summarizer = Summerizer("./test_data/stop_words.txt")
        doc_id = 'FBIS3-29'
        file_name = dicts.docs_dict[doc_id]['file_name'].strip()
        r = ReadFile()
        docs = r.read_file_from_path("./test_data/corpus/", file_name)
        doc = list(filter(lambda d: d.id == doc_id, docs))[0]
        res = summarizer.get_importent_sentences(doc, 5)
        pass


if __name__ == '__main__':
    unittest.main()
