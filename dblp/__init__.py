import xmltodict
import requests

_DBLP_BASE_URL = 'http://dblp.uni-trier.de/'
_DBLP_AUTHOR_SEARCH_URL = _DBLP_BASE_URL + 'search/author'

_DBLP_PERSON_URL = _DBLP_BASE_URL + 'pers/xk/{urlpt}'
_DBLP_PUBLICATION_URL = _DBLP_BASE_URL + 'rec/bibtex/{key}.xml'


def _first_or_none(pdict, name):
    try:
        return pdict[name]
    except KeyError:
        pass


class _LazyAPIData(object):
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


class Author(_LazyAPIData):
    def __init__(self, urlpt):
        self.urlpt = urlpt
        self.xml = None
        super(Author, self).__init__(
            ['name', 'publications', 'homepages', 'homonyms', 'dict']
        )

    def __eq__(self, other):
        return self.urlpt == other.urlpt

    def __ne__(self, other):
        return not self.__eq__(other)

    def load_data(self):
        resp = requests.get(_DBLP_PERSON_URL.format(urlpt=self.urlpt))
        xml = resp.content
        self.xml = xml

        temp_dict = xmltodict.parse(self.xml)
        temp_person_record = temp_dict['dblpperson']['dblpkey'][0]
        temp_pubs = temp_dict['dblpperson']['dblpkey'][1:len(temp_dict['dblpperson']['dblpkey'])]

        data = {
            'name': temp_dict['dblpperson']['@name'],
            'publications': [Publication(key) for key in temp_pubs],
            'homepages': temp_person_record['#text'],
            'homonyms': _first_or_none(temp_dict['dblpperson'], 'homonyms')
        }
        self.data = data


class Publication(_LazyAPIData):
    def __init__(self, key):
        self.key = key
        self.xml = None
        super(Publication, self).__init__(
            [
                'type', 'sub_type', 'mdate',
                'authors', 'editors', 'title', 'year', 'month', 'journal',
                'volume', 'number', 'chapter', 'pages', 'ee', 'isbn', 'url',
                'booktitle', 'crossref', 'publisher', 'school', 'citations',
                'series', 'key'
            ]
        )

    def __eq__(self, other):
        return self.key == other.key

    def __ne__(self, other):
        return not self.__eq__(other)

    def load_data(self):
        resp = requests.get(_DBLP_PUBLICATION_URL.format(key=self.key))
        xml = resp.content
        self.xml = xml

        publication = xmltodict.parse(self.xml)['dblp']
        type = list(publication.keys())[0]
        tempdict = publication[type]
        data = {
            'type': list(publication.keys())[0],
            'key': _first_or_none(tempdict, '@key'),
            'mdate': _first_or_none(tempdict, '@mdate'),
            'authors': tempdict['author'],
            'editors': _first_or_none(tempdict, 'editor'),
            'title': _first_or_none(tempdict, 'title'),
            'year': int(_first_or_none(tempdict, 'year')),
            'month': _first_or_none(tempdict, 'month'),
            'journal': _first_or_none(tempdict, 'journal'),
            'volume': _first_or_none(tempdict, 'volume'),
            'number': _first_or_none(tempdict, 'number'),
            'chapter': _first_or_none(tempdict, 'chapter'),
            'pages': _first_or_none(tempdict, 'pages'),
            'ee': _first_or_none(tempdict, 'ee'),
            'isbn': _first_or_none(tempdict, 'isbn'),
            'url': _first_or_none(tempdict, 'url'),
            'booktitle': _first_or_none(tempdict, 'booktitle'),
            'crossref': _first_or_none(tempdict, 'crossref'),
            'publisher': _first_or_none(tempdict, 'publisher'),
            'school': _first_or_none(tempdict, 'school')
            # 'citations':[Citation(c.text, c.attrib.get('label',None))
            #              for c in publication.xpath('cite') if c.text != '...'],
            # 'series':_first_or_none(Series(s.text, s.attrib.get('href', None))
            #           for s in publication.xpath('series'))
        }
        self.data = data


def search(author_str):
    resp = requests.get(_DBLP_AUTHOR_SEARCH_URL, params={'xauthor': author_str})

    tempdict = xmltodict.parse(resp.content)
    return [Author(author['@urlpt']) for author in tempdict['authors']['author']]
