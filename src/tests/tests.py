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

    def test_is_10K(self):
        """
        Test PDF object to see if it is a 10-K report
        """
        pdf = '/test-resources/test.pdf'
        pdf_bytes = open(pdf, 'rb')
        pdfObj = StockDropScraper.PDF(pdf_bytes, 'test.pdf')
        self.assertTrue(pdfObj.is_10K())


if __name__ == '__main__':
    unittest.main()

