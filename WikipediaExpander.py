import random
import wikipedia

class WikipediaExpander:
    def expand(self, query):
        '''
        add words to query from wikipedia
        :param query: query
        :return: expended query
        '''
        query = query .strip()
        if len(query.split(' ')) > 1:
            return query
        expended_query = [query]
        try:
            page = wikipedia.page(query)
        except wikipedia.DisambiguationError as e:
            page = wikipedia.page(e.options[0])
        add_terms = 4
        if len(page.links) <= add_terms:
            expended_query.extend(page.links)
        else:
            expended_query.extend(random.sample(page.links, add_terms))
        return " ".join(expended_query)
