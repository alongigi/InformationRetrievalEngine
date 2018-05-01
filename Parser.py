import os
import re
from collections import Counter, deque
from datetime import datetime


class Parser:
    def __init__(self, stop_word_path):
        self.contain_number = re.compile(".*\d.*")
        self.redundant_signs = ["|", "@", "^", "!", "?", "*", ";", "'", "\\", '"', '&', ':', '(', ')', '+', '=', '÷',
                                ']', '[', '\n', '\t', '#', ' %', '`', 'כ', 'ז', 'ף', 'ר', 'ד', 'כ', '}', 'ק', 'ם', '_']
        self.months = {"january", "february", "march", "april", "may", "june", "july", "august", "september", "october",
                       "november", "december", "jan", "feb", "mar", "apr", "jun", "jul", "aug", "sep", "oct", "nov",
                       "dec"}
        self.normal_date = re.compile("\d+/\d+|\d+/\d+/\d+")
        self.stop_words = self._set_of_stopwords(stop_word_path)

    def _set_of_stopwords(self, path):
        '''
        create set of words from stop-words file
        :param path: path to stop-word file
        :return: set of stop-words
        '''
        if not os.path.exists(path):
            return set()
        with open(path) as f:
            return set((line.strip() for line in f.readlines()))

    def parse(self, text):
        '''
        parse text to terms
        :param text: input text
        :return: Counter of the terms in the text => {term: frequency-in-text}
        '''
        for sign in self.redundant_signs:
            text = text.replace(sign, ' ')
        text = text.replace(",", '')
        text = text.replace(' .', ' ').replace('. ', ' ')
        raw_terms = text.split(' ')
        not_parsed_terms = self._parse_terms(raw_terms)
        self._parse_terms(not_parsed_terms)
        raw_terms.extend(not_parsed_terms)
        raw_terms = map(lambda x: x.strip(), raw_terms)
        raw_terms = deque(
            filter(lambda x: len(x) > 1 and x not in self.stop_words and x[0] not in {'.', '$', '/'}, raw_terms))
        return Counter(raw_terms)

    def _parse_terms(self, raw_terms):
        '''
        invoke parser rules on raw_terms, change the input list
        :param raw_terms: terms splited by space
        :return: terms that added form the parser rules and need to be parsed also, empty if there aren't any
        '''
        added_terms = deque()
        self._parse_numbers(raw_terms, added_terms)
        self._parse_dates(raw_terms)
        self._remove_dot_from_terms(raw_terms)
        self._parse_upper_case(raw_terms, added_terms)
        self._parse_dash(raw_terms, added_terms)
        return added_terms

    def _remove_dot_from_terms(self, raw_terms):
        '''
        remove dot in the end of terms
        '''
        for i, term in enumerate(raw_terms):
            if len(term) > 0 and term[len(term) - 1] == '.':
                raw_terms[i] = term[:-1]

    def _parse_dash(self, raw_terms, added_terms):
        '''
        parse terms containing '-'
        :param raw_terms: input terms, change the input
        :param added_terms: fill with extra terms parsed from original terms
        '''
        for i, term in enumerate(raw_terms):
            if '-' in term:
                splited_terms = term.split('-')
                raw_terms[i] = splited_terms[0]
                if not self.contain_number.match(splited_terms[0]) and not self.contain_number.match(splited_terms[1]):
                    added_terms.append((splited_terms[0] + ' ' + splited_terms[1]).lower())
                [added_terms.append(t.lower()) for t in splited_terms[1:]]

    def _parse_upper_case(self, raw_terms, added_terms):
        '''
        parse terms with starting with uppercase
        :param raw_terms: input terms, change the input
        :param added_terms: fill with extra terms parsed from original terms
        '''
        for i, term in enumerate(raw_terms):
            if len(term) > 0 and term[0].isupper():
                if i + 1 < len(raw_terms) and len(raw_terms[i + 1]) > 0 and raw_terms[i + 1][0].isupper():
                    added_terms.append((term + ' ' + raw_terms[i + 1]).lower())
                    raw_terms[i + 1] = raw_terms[i + 1].lower()
                raw_terms[i] = term.lower()
            else:
                raw_terms[i] = term.lower()

    def _parse_dates(self, raw_terms):
        '''
        parse term that are parts of a date
        :param raw_terms: input terms, change the input
        '''
        for i, term in enumerate(raw_terms):
            if term.lower() in self.months:
                date = []
                if i - 1 >= 0 and raw_terms[i - 1].replace('th', '').isdigit():
                    date.append(raw_terms[i - 1].replace('th', ''))
                    raw_terms[i - 1] = ''
                date.append(term)
                if i + 1 < len(raw_terms) and raw_terms[i + 1].replace('th', '').isdigit():
                    date.append(raw_terms[i + 1].replace('th', ''))
                    raw_terms[i + 1] = ''
                if len(date) < 3 and i + 2 < len(raw_terms) and raw_terms[i + 2].isdigit():
                    date.append(raw_terms[i + 2])
                    raw_terms[i + 2] = ''
                raw_terms[i] = self._parse_date(' '.join(date))

    def _parse_numbers(self, raw_terms, added_terms):
        '''
        parse term containing numbers
        :param raw_terms: input terms, change the input
        :param added_terms: fill with extra terms parsed from original terms
        '''
        for i, term in enumerate(raw_terms):
            if self.contain_number.match(term) and not term.isdigit():
                try:
                    if term.isdigit():
                        continue
                    elif '/' in term:
                        if self.normal_date.match(term):
                            raw_terms[i] = term
                        else:
                            [added_terms.append(term) for term in term.split('/')]
                            raw_terms[i] = ''
                    elif '$' in term:
                        if re.match("\$\d+b.*|\$\d+\.\d+b.*", term):
                            raw_terms[i] = (term[term.find("$") + 1:term.find("b")] + " dollar")
                            added_terms.append("billion")
                        elif re.match("\$\d+m.*|\$\d+\.\d+m.*", term):
                            raw_terms[i] = (term[term.find("$") + 1:term.find("m")] + " dollar")
                            added_terms.append("million")
                        else:
                            term = term[term.find("$") + 1:]
                            term = term.replace('$', '')
                            if '-' in term:
                                res = term.split('-')
                                raw_terms[i] = self._parse_number(res[0]) + " dollar"
                                added_terms.append(res[1])
                            else:
                                raw_terms[i] = self._parse_number(term) + " dollar"
                    elif '%' in term:
                        raw_terms[i] = (self._parse_percentage(term, '%'))
                    else:
                        raw_terms[i] = self._parse_number(raw_terms[i])
                except ValueError:
                    pass
            elif term.startswith('percent'):
                if i - 1 >= 0 and self._is_number(raw_terms[i - 1]):
                    raw_terms[i] = raw_terms[i - 1] + ' percent'
                    raw_terms[i - 1] = ''
        return added_terms

    def _parse_percentage(self, term, type):
        '''
        parse term that represent percentage
        :param term: term
        :param type: can be {%, percent, percentage}
        :return: the parsed term
        '''
        return self._parse_number(term.replace(type, '')) + ' percent'

    def _parse_number(self, token):
        '''
        parse term that represent number
        :return: the parsed term
        '''
        return self._parse_float(float(token))

    def _parse_date(self, token):
        '''
        parse term as parsed date at format dd/mm/yyyy or dd/mm or mm/yyyy
        :return: the date term
        '''
        try:
            if '/' in token:
                return token
            token = token.replace('th', '')
            return self._parse_day_month_year_date(token)
        except Exception:
            return token

    def _parse_day_month_year_date(self, token):
        '''
        parse string containing day month year
        '''
        input_format = ''
        output_format = ''
        date = token.split(' ')
        if self._is_number(date[0]):
            input_format, output_format = self._day_first(date, input_format, output_format)
        else:
            input_format, output_format = self._month_first(date, input_format, output_format)
        if len(date) > 2:
            year = date[2]
            input_format, output_format = self._year_last(year, input_format, output_format)

        return self._parse_date_by_format(token, input_format, output_format)

    def _month_first(self, date, input_format, output_format):
        '''
        parse date when month appear first
        '''
        month = date[0]
        output_format += '%m'
        if len(month) > 3:
            input_format += '%B'
        else:
            input_format += '%b'
        if len(date[1]) <= 2 and int(date[1]) <= 31:
            input_format += ' %d'
            output_format = "%d/" + output_format
        else:
            year = date[1]
            input_format, output_format = self._year_last(year, input_format, output_format)
        return input_format, output_format

    def _year_last(self, year, input_format, output_format):
        '''
        parse date when year appear last
        '''
        output_format += "/%Y"
        if len(year) <= 2:
            input_format += ' %y'
        else:
            input_format += ' %Y'
        return input_format, output_format

    def _day_first(self, date, input_format, output_format):
        '''
        parse date when day appear first
        '''
        input_format += '%d'
        output_format += '%d/%m'
        month = date[1]
        if len(month) > 3:
            input_format += ' %B'
        else:
            input_format += ' %b'
        return input_format, output_format

    def _parse_date_by_format(self, token, input_format, output_format):
        '''
        parse token in the input format to token in the output format
        '''
        return datetime.strptime(token, input_format).strftime(output_format)

    def _parse_float(self, f):
        '''
        parse string that represent float
        :return: the float fix with 2 digits after the floating point
        '''
        frac_result = str(format(f, ".2f"))
        return frac_result.replace('.00', '')

    def _is_month(self, raw_term):
        '''
        :return: True if input term is a month name
        '''
        return raw_term.lower() in self.months

    def _is_number(self, raw_term):
        '''
        :return: True if intup term is a number
        '''
        if raw_term.replace('.', '').isdigit():
            return True
        return False
