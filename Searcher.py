from Parser import Parser
from Ranker import Ranker
from Stemmer import Stemmer


class Searcher:
    def __init__(self, stop_word_path, term_dict, doc_dict, cache, term_posting_file):
        self.parser = Parser(stop_word_path)
        self.stemmer = Stemmer()
        self.ranker = Ranker(term_dict, doc_dict, cache, term_posting_file)
        # self.to_stem = to_stem

    def search_query(self, query, to_stem=False, limit=50):
        '''
        search relevant documents to query
        :param query: query to search
        :param to_stem: true to activate stemming
        :param limit: limit relevant documents
        :return: relevant documents to query
        '''
        terms = self.parser.parse(query)
        if to_stem:
            terms = self.stemmer.stem(terms)
        return list(self.ranker.rank_query(terms, limit))
