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
