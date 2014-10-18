import dblp
import unittest

class Tests(unittest.TestCase):
    def test_query_author(self) -> None:
        authors = dblp.search('james fogarty')
        self.assertGreater(len(authors), 0)
        self.assertIn(dblp.Author('f/Fogarty:James'), authors)
