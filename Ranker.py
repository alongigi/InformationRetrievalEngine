import math
from sortedcollections import SortedList
from collections import Counter

from Indexer import Indexer


class Ranker:
    def __init__(self, term_dict, doc_dict, cache, term_posting_file):
        self.term_dict = term_dict
        self.doc_dict = doc_dict
        self.cache = cache
        self.N = len(doc_dict)
        self.term_posting_file = term_posting_file
        self.indexer = Indexer()

    def rank_query(self, query, result_limit=50):
        '''
        rank relevant documents to query
        :param query: query to search
        :param limit: limit relevant documents
        :return: ranked relevant documents to query
        '''
        docs = []
        most_common_docs = Counter()
        f = open(self.term_posting_file, 'r')
        word_to_delete = []
        for word in query:
            if word in self.cache:
                docs.extend(self.cache[word]['docs'].split('*')[:-1])
            elif word in self.term_dict:
                row = self.term_dict[word]['row']
                term, term_data = self.indexer.getTermAndTermData(f, row)
                docs.extend(term_data['docs'].split('*')[:-1])

        query = list(filter(lambda w: w in self.term_dict, query))
        f.close()
        for d in docs:
            doc_id, frec = d.split(':')
            most_common_docs[doc_id] = self.calculate_cossim(query, d)
        result = map(lambda x: x[0], most_common_docs.most_common(result_limit))
        return result

    def calculate_tfidf(self, word, document):
        '''
        Calculate tfidf
        :param word: word for calculation
        :param document: document for calculation
        :return: tf * idf
        '''
        doc_id, frec = document.split(':')
        frec = int(frec)
        D = self.doc_dict[doc_id]['doc_size']
        tf = frec / D
        df = self.term_dict[word]['df']
        idf = math.log2(self.N / df)
        return tf * idf

    def calculate_cossim(self, query, document):
        '''
        Calculate cossim
        :param query: query for calculation
        :param document: document for calculation
        :return: cossim
        '''
        doc_id, frec = document.split(':')
        innerproduct = 0
        for word in query:
            word_w = self.calculate_tfidf(word, document)
            innerproduct += word_w
        doc_w = self.doc_dict[doc_id]['W']
        denominator = math.sqrt(len(query) * doc_w)

        return innerproduct / denominator
