import unittest

from Stemmer import Stemmer


class StemmerTest(unittest.TestCase):
    def setUp(self):
        self.stemmer = Stemmer()

    def test_steming_dict_2(self):
        t = {"read": 3, "reading": 4, "take": 2}
        result = self.stemmer.stem_term_dict(t)
        expected = {"read": 7, "take": 2}
        self.assertDictEqual(result, expected)
