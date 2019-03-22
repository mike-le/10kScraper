import unittest
from src.main import StockDropScraper


class TestScraper(unittest.TestCase):
    def test_HTTP_get(self):
        """
        Test response receives 200 code and has content-type
        """
        url = 'https://www.thewaltdisneycompany.com/investor-relations/'
        result = True if StockDropScraper.simple_get(url) is not None else False
        self.assertTrue(result)


if __name__ == '__main__':
    unittest.main()

