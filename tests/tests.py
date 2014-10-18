import dblp
import unittest


class Tests(unittest.TestCase):
    def test_query_author(self) -> None:
        authors = dblp.search('james fogarty')
        self.assertGreater(len(authors), 0)
        self.assertIn(dblp.Author('f/Fogarty:James'), authors)

    def test_query_publications(self) -> None:
        publications = dblp.Author('f/Fogarty:James').publications
        self.assertGreater(len(publications), 0)

        self.assertIn(dblp.Publication('conf/avi/HipkeTFF14'), publications)
        self.assertIn(dblp.Publication('conf/chi/AmershiFKT10'), publications)
        self.assertIn(dblp.Publication('conf/uist/AdarDFW08'), publications)
        self.assertIn(dblp.Publication('conf/uist/FogartyFH01'), publications)

    def test_query_publication_data(self) -> None:
        pub = dblp.Publication('conf/chi/AmershiFKT10')
        self.assertEquals(pub.authors, ['Saleema Amershi', 'James Fogarty', 'Ashish Kapoor', 'Desney S. Tan'])
        self.assertEquals(pub.title, 'Examining multiple potential models in end-user interactive concept learning.')
        self.assertEquals(pub.year, 2010)
