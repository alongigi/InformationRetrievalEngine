import os
from collections import Counter, defaultdict

import math
from sortedcollections import SortedDict


class Indexer:
    def __init__(self, path=""):
        # self.doc_weghits = defaultdict()
        self.TermDictionary = {}
        self.DocsDictionary = defaultdict()
        self.Cache = {}
        self.terms_output_file = ''
        self.docs_output_file = "merged_docs.p"
        open(self.docs_output_file, 'w').close()

        self.docs_posting = []
        self.terms_posting = []
        self.term_to_doc_id = SortedDict()
        self.path = path
        self._index = 0
        self.message = "\n"

    def index_terms(self, terms_dict, doc):
        '''
        index terms for posting and sort them in self.term_to_doc_id {SortedDict()} , sort by term
        and index docs for posting and save them in self.docs_posting
        :param terms_dict: terms from document
        :param doc: the document
        '''
        if len(terms_dict) == 0:
            return
        most_frequent = str(max(terms_dict, key=terms_dict.get))

        doc_row = "{0}#{1}#{2}#{3}#{4}\n".format(doc.id, most_frequent, terms_dict[most_frequent], str(len(doc.text)),
                                                 doc.file_name)
        self.docs_posting.append(doc_row)

        for term in terms_dict:
            if term not in self.term_to_doc_id:
                self.term_to_doc_id[term] = {}
            self.term_to_doc_id[term][doc.id] = terms_dict[term]

    def clean_postings(self):
        '''
        delete posting files
        '''
        postings_files = list(os.listdir(self.path))
        for f in postings_files:
            os.remove(self.path + f)

    def flush(self):
        '''
        write the terms sorted in self.term_to_doc_id to temp terms posting file
        and write the docs from self.docs_posting to temp doc posting file
        '''
        for term in self.term_to_doc_id:
            term_row = term + "#" + str(len(self.term_to_doc_id[term])) + "#"
            sum_tf = 0
            docs_list = ""
            for doc in self.term_to_doc_id[term]:
                sum_tf += self.term_to_doc_id[term][doc]
                docs_list += "{0}:{1}*".format(doc, self.term_to_doc_id[term][doc])
            term_row += str(sum_tf) + "#"
            term_row += docs_list
            term_row += '\n'
            self.terms_posting.append(term_row)

        if len(self.terms_posting) > 0:
            f_terms = open("{0}{1}_terms.t".format(self.path, str(self._index)), 'w')
            f_terms.writelines(self.terms_posting)
            f_terms.close()

        if len(self.docs_posting) > 0:
            f_docs = open(self.path + "merged_docs.p", 'a')
            f_docs.writelines(self.docs_posting)
            f_docs.close()

        self.docs_posting = []
        self.terms_posting = []
        self.term_to_doc_id = SortedDict()
        self._index += 1

    def merge_docs_postings(self, docs_output_file):
        '''
        set the merge doc posting file name as @docs_output_file
        '''
        if docs_output_file != self.docs_output_file:
            open(self.path + docs_output_file, 'w').close()
            os.remove(self.path + docs_output_file)
            os.rename(self.path + self.docs_output_file, self.path + docs_output_file)
            self.docs_output_file = docs_output_file

    def merge_terms_postings(self, terms_output_file):
        '''
        merge term posting
        '''
        self.terms_output_file = terms_output_file
        files_names = list(filter(lambda f: f.endswith("terms.t"), os.listdir(self.path)))
        num = 1
        while len(files_names) > 1:
            file1 = files_names[len(files_names) - 2]
            file2 = files_names[len(files_names) - 1]
            self.merge_files(open(self.path + file1), open(self.path + file2), "merged" + str(num) + "_terms.t")
            os.remove(self.path + file1)
            os.remove(self.path + file2)
            files_names = list(filter(lambda f: f.endswith("terms.t"), os.listdir(self.path)))
            num += 1
        open(self.path + self.terms_output_file, 'w').close()
        os.remove(self.path + self.terms_output_file)
        os.rename(self.path + files_names[0], self.path + self.terms_output_file)

    def merge_files(self, file1, file2, output):
        '''
        merge 2 sorted temp term posting file , read up to 3 lines from each file
        :param output: name of output file
        '''
        d = []
        file1_lines_count = 0
        file2_lines_count = 0
        file1_line = file1.readline()
        file1_lines_count += 1
        file2_line = file2.readline()
        file2_lines_count += 1
        output_file = open(self.path + output, 'w')
        while file1_line != '':
            term1, freq1, sum_tf1, doc_list1 = file1_line.split('#')
            term2, freq2, sum_tf2, doc_list2 = file2_line.split('#')
            if term1 < term2:
                d.append(file1_line)
                file1_line = file1.readline()
                file1_lines_count += 1
            elif term2 < term1:
                d.append(file2_line)
                file2_line = file2.readline()
                file2_lines_count += 1
                if file2_line == '':
                    break
            else:
                term2, freq2, sum_tf2, doc_list2 = file2_line.split('#')
                freq = int(freq1) + int(freq2)
                doc_list = doc_list1.rstrip() + doc_list2
                sum_tf = int(sum_tf1) + int(sum_tf2)
                d.append('#'.join([term1, str(freq), str(sum_tf), doc_list]))
                file1_line = file1.readline()
                file1_lines_count += 1
                # if file1_line == '':
                #     break
                file2_line = file2.readline()
                file2_lines_count += 1
                if file2_line == '':
                    break
            if file1_lines_count == 3 or file2_lines_count == 3:
                output_file.writelines(d)
                d = []
                file1_lines_count = 0
                file2_lines_count = 0

        while file2_line != '':
            d.append(file2_line)
            file2_line = file2.readline()
            file2_lines_count += 1
            if file2_lines_count == 3:
                output_file.writelines(d)
                d = []
                file2_lines_count = 0
        output_file.writelines(d)

        file1.close()
        file2.close()
        output_file.close()

    def get_data_from_doc_posting_line(self, line, file_row):
        '''
        retrieve data from doc posting
        '''
        doc_id, most_frequent_term, term_count, doc_size, file_name = line.split('#')
        doc_data = {'row': file_row, 'most_ferc_term': most_frequent_term, 'term_count': term_count,
                    'doc_size': int(doc_size), 'file_name': file_name.strip()}
        return doc_id, doc_data

    def get_data_from_term_posting_line(self, line, file_row):
        '''
        retrieve data from term posting
        '''
        term, df, sum_tf, docs = line.split('#')
        term_data = {'row': file_row, 'sum_tf': sum_tf, 'df': int(df), 'docs': docs}
        return term, term_data

    def get_term_dictionary(self):
        '''
        create term dictionary, build it only once
        :return: the term dict
        '''
        doc_dict = self.get_doc_dictionary()
        doc_weight = Counter()
        if self.TermDictionary != {}:
            return self.TermDictionary
        with open(self.path + self.terms_output_file, 'r+') as f:
            file_pos = f.tell()
            line = f.readline()
            while line:
                term, term_data = self.get_data_from_term_posting_line(line, file_pos)
                file_pos = f.tell()
                line = f.readline()
                term_frec_in_doc = map(lambda x: x.split(':'), term_data['docs'].split('*')[:-1])
                N = len(doc_dict)
                df = term_data['df']
                for t in term_frec_in_doc:
                    fi = int(t[1])
                    D_len = doc_dict[t[0]]['doc_size']
                    tfidf = (fi / D_len) * math.log(N / df, 2)
                    doc_weight[t[0]] += tfidf
                term_data.pop('docs')
                self.TermDictionary[term] = term_data

        for doc in self.DocsDictionary:
            self.DocsDictionary[doc]['W'] = doc_weight[doc]

        return self.TermDictionary

    def get_doc_dictionary(self):
        '''
        create doc dictionary, build it only once
        :return: the doc dict
        '''

        if self.DocsDictionary != {}:
            return self.DocsDictionary
        f = open(self.path + self.docs_output_file, 'r')
        for i, line in enumerate(f):
            doc_id, doc_data = self.get_data_from_doc_posting_line(line, i + 1)
            self.DocsDictionary[doc_id] = doc_data
        return self.DocsDictionary

    def create_cache(self, limit):
        '''
        generate cach from term dictionary
        :param limit: the limit of terms in cache
        :return: the cache dict
        '''
        term_frequency = Counter()
        for term in self.TermDictionary:
            term_frequency[term] = self.TermDictionary[term]['df']

        most_common_terms = term_frequency.most_common(limit)
        f = open(self.path + self.terms_output_file, 'r')
        for term, frec in most_common_terms:
            row = self.TermDictionary[term]['row']
            term, term_data = self.getTermAndTermData(f, row)
            term_data.pop('sum_tf')
            term_data.pop('df')
            cache_limit = 50

            splited_docs = term_data['docs'].split('*')
            if len(splited_docs) > cache_limit:
                c = Counter()
                for doc in splited_docs[:-1]:
                    doc_id, tf = doc.split(':')
                    c[doc] = tf
                term_data['docs'] = '*'.join(map(lambda x: x[0], c.most_common(cache_limit))) + '@'
                # @ means that there more docs in postings
            self.Cache[term] = term_data
            self.TermDictionary[term]['row'] = -1
        f.close()
        return self.Cache

    def getTermAndTermData(self, f, row):
        """
        get the term and the term data from a row in the term posting
        :param f: file object of the posting
        :param row: position in the file to the start of the line
        :return: term and term data(posting data)
        """
        f.seek(row)
        line = f.readline().rstrip()
        term, term_data = self.get_data_from_term_posting_line(line, row)
        return term, term_data