# import dblp
import xmltodict
import requests
from collections import namedtuple
# from lxml import etree

DBLP_BASE_URL = 'http://dblp.uni-trier.de/'
DBLP_AUTHOR_SEARCH_URL = DBLP_BASE_URL + 'search/author'

DBLP_PERSON_URL = DBLP_BASE_URL + 'pers/xk/{urlpt}'
DBLP_PUBLICATION_URL = DBLP_BASE_URL + 'rec/bibtex/{key}.xml'


class LazyAPIData(object):

    def __init__(self, lazy_attrs):
        self.lazy_attrs = set(lazy_attrs)
        self.data = None

    def __getattr__(self, key):
        if key in self.lazy_attrs:
            if self.data is None:
                self.load_data()
            return self.data[key]
        raise AttributeError(key)

    def load_data(self):
        pass


class Author(LazyAPIData):
    def __init__(self, urlpt):
        self.urlpt = urlpt
        self.xml = None
        super(Author, self).__init__(['name', 'publications', 'homepages',
                                      'homonyms', 'dict'])

    def __eq__(self, other):
        return self.urlpt == other.urlpt

    def __ne__(self, other):
        return not self.__eq__(self, other)

    def load_data(self):
        resp = requests.get(DBLP_PERSON_URL.format(urlpt=self.urlpt))
        xml = resp.content
        self.xml = xml

        tempdict = xmltodict.parse(self.xml)
        data = {
            'name': tempdict['dblpperson']['@name'],
            'publications': [Publication(k) for k in tempdict['dblpperson']['dblpkey'][1:len(tempdict['dblpperson']['dblpkey'])]],
            'homepages': tempdict['dblpperson']['dblpkey'][0]['#text'],
            'homonyms': first_or_none(tempdict['dblpperson'], 'homonyms')
        }
        self.data = data


def first_or_none(pdict, name):
    try:
        return pdict[name]
    except KeyError:
        pass


class Publication(LazyAPIData):

    def __init__(self, key):
        self.key = key
        self.xml = None
        super(Publication, self).__init__(['type', 'sub_type', 'mdate',
                                           'authors', 'editors', 'title', 'year', 'month', 'journal',
                                           'volume', 'number', 'chapter', 'pages', 'ee', 'isbn', 'url',
                                           'booktitle', 'crossref', 'publisher', 'school', 'citations',
                                           'series', 'key'])

    def load_data(self):
        resp = requests.get(DBLP_PUBLICATION_URL.format(key=self.key))
        xml = resp.content
        self.xml = xml

        publication = xmltodict.parse(self.xml)['dblp']
        tempdict = publication[list(publication.keys())[0]]
        data = {
            'type': list(publication.keys())[0],
            'key': first_or_none(tempdict, '@key'),
            'mdate': first_or_none(tempdict, '@mdate'),
            'authors': tempdict['author'],
            'editors': first_or_none(tempdict, 'editor'),
            'title': first_or_none(tempdict, 'title'),
            'year': int(first_or_none(tempdict, 'year')),
            'month': first_or_none(tempdict, 'month'),
            'journal': first_or_none(tempdict, 'journal'),
            'volume': first_or_none(tempdict, 'volume'),
            'number': first_or_none(tempdict, 'number'),
            'chapter': first_or_none(tempdict, 'chapter'),
            'pages': first_or_none(tempdict, 'pages'),
            'ee': first_or_none(tempdict, 'ee'),
            'isbn': first_or_none(tempdict, 'isbn'),
            'url': first_or_none(tempdict, 'url'),
            'booktitle': first_or_none(tempdict, 'booktitle'),
            'crossref': first_or_none(tempdict, 'crossref'),
            'publisher': first_or_none(tempdict, 'publisher'),
            'school': first_or_none(tempdict, 'school')
            # 'citations':[Citation(c.text, c.attrib.get('label',None))
            #              for c in publication.xpath('cite') if c.text != '...'],
            # 'series':first_or_none(Series(s.text, s.attrib.get('href', None))
            #           for s in publication.xpath('series'))



        }
        self.data = data


def search(author_str):
    resp = requests.get(DBLP_AUTHOR_SEARCH_URL, params={'xauthor': author_str})
    # TODO error handling
    # print resp.content
    tempdict = xmltodict.parse(resp.content)
    authors = []
    for adict in tempdict['authors']['author']:
        authors.append(Author(adict['@urlpt']))
    return authors
    # root = etree.fromstring(resp.content)
    # return [Author(urlpt) for urlpt in root.xpath('/authors/author/@urlpt')]
