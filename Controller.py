from threading import Thread

import time

from Model import Model
from Observable import Observable
from Observer import Observer
from ReadFile import ReadFile
from Searcher import Searcher
from Summarizer import Summarizer
from WikipediaExpander import WikipediaExpander


class Dictionary:
    def __init__(self, term_dict, docs_dict):
        self.term_dict = term_dict
        self.docs_dict = docs_dict


class Controller(Observer, Observable):
    def __init__(self):
        Observable.__init__(self)
        self.module = None
        self.term_dict = {}
        self.docs_dict = {}
        self.cache = {}
        self.query_results = []
        self.posting_path = ""
        self.doc_path = ""

    def start_indexing(self, doc_path, posting_path, stem):
        '''
        start the indexing process for creating Dictionary and Postings files
        :param doc_path: path of the corpus
        :param posting_path: path where posting will be saved
        :param stem: True for activating stemming
        '''
        print("Stemming: {0}".format(stem))
        self.module = Model(doc_path, posting_path)
        self.module.set_observer(self)
        t = Thread(target=self.module.run_process, args=(stem, 200))
        t.start()

    def clean_postings(self):
        '''
        delete posting cache and dictionary files from postings path
        '''
        self.term_dict = {}
        self.docs_dict = {}
        self.cache = {}
        if self.module is not None:
            self.module.clean_indexing()

    def get_dictionary(self):
        '''
        :return: the Dictionary
        '''
        d = Dictionary(self.term_dict, self.docs_dict)
        # return self.term_dict
        return d

    def get_cache(self):
        '''
        :return: the Cache
        '''
        return self.cache

    def get_results(self):
        '''
        :return: the Cache
        '''
        return self.query_results

    def set_cache(self, cache):
        '''
        set the cache
        '''
        self.cache = cache

    def set_dictionary(self, dictionary):
        '''
        set the dictionary
        '''
        self.docs_dict = dictionary.docs_dict
        self.term_dict = dictionary.term_dict

    def update(self, **kwargs):
        '''
        get updates from the Model
        '''
        if "fail" in kwargs:
            self.notify_observers(**kwargs)
        elif kwargs['done']:
            self.term_dict = self.module.get_term_dictionary()
            self.docs_dict = self.module.get_doc_dictionary()
            self.cache = self.module.get_cache()
            self.notify_observers(status="Done!!!", done=True, progress=0, summary=kwargs['summary'])
        else:
            self.notify_observers(**kwargs)

    # def check_search_preconditions(self):
    #     return self.doc_path != ""

    def search_query(self, query, query_num=0, stem=False, limit=50):
        '''
        search relevant documents to query
        :param query: query
        :param query_num: query number
        :param stem: true to activate stemming
        :param limit: limit relevant documents
        :return query result
        :return time of process
        '''
        start = time.time()
        d = self.get_dictionary()
        postings_postfix = "/merged_terms_postings"
        if stem:
            postings_postfix = "/stemed_merged_terms_postings"
        self.searcher = Searcher(self.doc_path + "/stop_words.txt", d.term_dict,
                                 d.docs_dict, self.get_cache(), self.posting_path + postings_postfix)
        self.query_results = {query_num: self.searcher.search_query(query, limit=limit, to_stem=stem)}
        totaltime = time.time() - start
        return self.query_results, totaltime

    def search_file_query(self, query_file, stem=False):
        '''
        search relevant documents to queries in file
        :param query_file: query file
        :param stem: true to activate stemming
        :return queries result
        :return time of process
        '''
        results = {}
        start = time.time()
        r = ReadFile()
        queries = r.read_query_file(query_file)
        query_num = 0
        for query in queries:
            query_num = queries[query]
            result, t_time = self.search_query(query, query_num, stem)
            results.update(result)
        totaltime = time.time() - start
        self.query_results = results
        return results, totaltime

    def save_query_results(self, file_result):
        '''
        save the query result to the memory
        :param file_result: file query
        '''
        for query_id in self.query_results:
            for doc_id in self.query_results[query_id]:
                file_result.write("{0}   0  {1}  1   42.38   mt\n".format(query_id, doc_id))

    def summarize_document(self, doc_id, docs_path):
        '''
        summarize the document
        :param doc_id: id of document
        :param docs_path: path of corpus
        :return most important sentences in documents
        '''
        summarizer = Summarizer(self.doc_path + "/stop_words.txt")
        if self.docs_dict == {}:
            raise Exception
        if doc_id not in self.docs_dict:
            return None
        file_name = self.docs_dict[doc_id]['file_name'].strip()
        r = ReadFile()
        t = "{0}/corpus/".format(docs_path)
        docs = r.read_file_from_path(t, file_name)
        doc = list(filter(lambda d: d.id == doc_id, docs))[0]
        res = summarizer.get_importent_sentences(doc, 5)
        return res

    def expand_query(self, query, query_num=0, stem=False):
        '''
        expand the query
        :param query: query
        :param query_num: query number
        :param stem: True for activating stemming
        :return queries result
        :return time of process
        '''
        wx = WikipediaExpander()
        expended_query = wx.expand(query)
        limit = 50
        if query != expended_query:
            limit = 70
        self.query_results, t_time = self.search_query(expended_query, query_num, stem, limit)
        if len(self.query_results[query_num]) < 51:
            self.query_results, t_time = self.search_query(query, query_num, stem, 50)
        return self.query_results, t_time
