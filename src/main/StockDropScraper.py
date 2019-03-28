from requests import get
from requests.exceptions import RequestException
from contextlib import closing
from bs4 import BeautifulSoup
from urllib import request, error
from PDF import PDF
import urllib
import os
import time
import json

_DIRECTORY = "../../target/generated-resources/"


def simple_get(url):
    """
    Attempts to get the content at `url` by making an HTTP GET request.
    If the content-type of response is some kind of HTML/XML, return the
    text content, otherwise return None.
    """
    try:
        with closing(get(url, stream=True)) as resp:
            if is_good_response(resp):
                return resp.content
            else:
                return None

    except RequestException as e:
        log_error('Error during requests to {0} : {1}'.format(url, str(e)))
        return None


def get_report(company):
    """
    Downloads the PDFs from the given url
    """
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
        TARGET_PATH = _DIRECTORY + _TICKER
        create_directory(TARGET_PATH)

        for name, url in names_urls:
            try:
                rq = urllib.request.urlopen(url)
                pdf = rq.read()
                header = str(rq.info())
                if 'Content-Disposition' in header or 'application/pdf' in header:
                    pdfObj = PDF(pdf, name)
                    if pdfObj.is_10K:
                        pdfYear = pdfObj.get_year()
                        year = str(pdfYear) if (pdfYear is not None) and (pdfYear > 0) else 'etc'
                        path = TARGET_PATH + '/' + year + '/'
                        create_directory(path)
                        with open(path+name, 'wb') as f:
                            f.write(pdf)
                            numberOfFiles += 1
            except error.HTTPError as e:
                if e.code == 404:
                    log_error('File not found during requests to {0} : {1}'.format(_URL, str(e)))
                else:
                    raise
        end = time.time()
        print(str(_TICKER))
        print('Execution Time: ' + str(round(end - start, 2)) + ' seconds')
        print('Number of files copied over: ' + str(numberOfFiles) + " out of " + str(numberOfUrls))
    else:
        # Raise an exception if we failed to get any data from the url
        log_error('error found for {}'.format(response))
        raise Exception('Error retrieving contents at {}'.format(_URL))


def is_good_response(resp):
    content_type = resp.headers['Content-Type'].lower()
    return (resp.status_code == 200
            and content_type is not None
            and content_type.find('html') > -1)


def create_directory(dir):
    if not os.path.exists(dir):
        os.makedirs(dir)


def log_error(e):
    print(e)


if __name__ == '__main__':
    try:
        with open("../tests/test-resources/testData.json", 'r') as f:
            datastore = json.load(f)
        for index, company in enumerate(datastore):
            get_report(company)
    except FileNotFoundError as e:
        log_error('JSON file not found: {0}'.format(str(e)))



