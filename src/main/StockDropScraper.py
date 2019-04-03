from requests import get
from requests.exceptions import RequestException
from contextlib import closing
from bs4 import BeautifulSoup
from urllib import request, error
from PDF import PDF
import logging
import urllib
import os
import time
import json

PDF_DIRECTORY = ""
LOG_DIRECTORY = ""
TEST_DIRECTORY = ""

"""
Attempts to get the content at `url` by making an HTTP GET request.
If the content-type of response is some kind of HTML/XML, return the
text content, otherwise return None.
"""
def simple_get(url):
    try:
        with closing(get(url, stream=True)) as resp:
            if is_good_response(resp):
                return resp.content
            else:
                return None

    except RequestException as e:
        logging.debug('Error during requests to {0} : {1}'.format(url, str(e)))
        return None

"""
Downloads the PDFs from the given url
"""
def get_report(company):
    urls = []
    names = []
    _TICKER = company["Ticker"]
    _DOMAIN = company["Domain"]
    _URL = company["URL"]
    response = simple_get(_URL)
    start = time.time()
    numberOfUrls = 0
    numberOfFiles = 0

    if response is not None:
        response = BeautifulSoup(response, 'html.parser')

        for i, link in enumerate(response.findAll('a')):
            _FULLURL = str(link.get('href'))
            _TYPE = str(link.get('type'))
            if 'pdf' in _TYPE or '.pdf' in _FULLURL:
                if not str(_FULLURL).startswith('http'):
                    _FULLURL = _DOMAIN + _FULLURL
                urls.append(_FULLURL)
                name = response.select('a')[i].attrs['href'].replace('/', '_')
                if '.com' in name:
                    name = name.split('.com')[1]
                if not name.endswith('.pdf'):
                    name = name + '.pdf'
                names.append(name)
                numberOfUrls += 1
        names_urls = zip(names, urls)

        # Create target folder if it does not exist
        TARGET_PATH = PDF_DIRECTORY + _TICKER
        create_directory(TARGET_PATH)

        for name, url in names_urls:
            try:
                rq = urllib.request.urlopen(url)
                pdf = rq.read()
                header = str(rq.info())
                if 'Content-Disposition' in header or 'application/pdf' in header:
                    pdfObj = PDF(pdf, name)
                    if PDF.is_10K(pdfObj):
                        pdfYear = PDF.get_year(pdfObj)
                        year = str(pdfYear) if (pdfYear is not None) and (pdfYear > 0) else 'etc'
                        path = TARGET_PATH + '/' + year + '/'
                        create_directory(path)
                        with open(path+name, 'wb') as f:
                            f.write(pdf)
                            numberOfFiles += 1
            except error.HTTPError as e:
                if e.code == 404:
                    logging.debug('File not found during requests to {0} : {1}'.format(_URL, str(e)))
                else:
                    raise
        end = time.time()
        logging.info('Ticker: ' + str(_TICKER))
        logging.info('Execution Time: ' + str(round(end - start, 2)) + ' seconds')
        logging.info('Number of files copied over: ' + str(numberOfFiles) + " out of " + str(numberOfUrls))
    else:
        # Raise an exception if we failed to get any data from the url
        logging.debug('Error found for {}'.format(response))
        raise Exception('Error retrieving contents at {}'.format(_URL))


def is_good_response(resp):
    content_type = resp.headers['Content-Type'].lower()
    return (resp.status_code == 200
            and content_type is not None
            and content_type.find('html') > -1)


def create_directory(dir):
    if not os.path.exists(dir):
        os.makedirs(dir)
        logging.info('Directory created at: ' + str(dir))


if __name__ == '__main__':
    
    try:
        with open('../../config.json') as configJSON:
            config = json.load(configJSON)
            LOG_DIRECTORY = config["directory"]["log"]
            PDF_DiRECTORY = config["directory"]["target"]
            TEST_DIRECTORY = config["directory"]["testsource"]
        logging.basicConfig(filename=LOG_DIRECTORY+'scraperlog.log', filemode='w', level=logging.DEBUG)
        logging.info('Initiated scraping...')
        with open(TEST_DIRECTORY+'testData.json', 'r') as f:
            datastore = json.load(f)
        for index, company in enumerate(datastore):
            get_report(company)
    except FileNotFoundError as e:
        logging.debug('JSON file not found: {0}'.format(str(e)))
    finally:
        logging.info('Finished')



