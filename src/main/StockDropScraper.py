from requests import get
from requests.exceptions import RequestException
from contextlib import closing
from bs4 import BeautifulSoup
from urllib import request, error
from PDF import PDF
from PyPDF2 import utils, PdfFileReader
import subprocess
import io
import logging
import urllib
import os
import time
import json
import sys

PDF_DIRECTORY, LOG_DIRECTORY, TEST_DIRECTORY = None

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
    _TICKER = company["Ticker"]
    _DOMAIN = company["Domain"]
    _URL = company["URL"]
    response = simple_get(_URL)
    start = time.time()
    urlcount, filecount = 0

    # Create dictionary of file names and links to all PDFs from response object
    names_urls = scrape_pdf_links(_URL, _DOMAIN, response, urlcount)

    # Create target folder if it does not exist
    TARGET_PATH = PDF_DIRECTORY + _TICKER
    create_directory(TARGET_PATH)

    # Validate PDF and save to target directory
    for name, url in names_urls:
        try:
            rq = urllib.request.urlopen(url)
            pdf = rq.read()
            header = str(rq.info())
            if 'Content-Disposition' in header or 'application/pdf' in header:
                pdfReader = PdfFileReader(io.BytesIO(pdf))
                pdfObj = PDF(pdfReader, name)
                if pdfObj.is_10K:
                    logging.debug('Files decrypted: ' + str(pdfObj.get_decryptCount()))
                    pdfYear = pdfObj.get_year()
                    year = str(pdfYear) if (pdfYear is not None) and (pdfYear > 0) else 'etc'
                    path = TARGET_PATH + '/' + year + '/'
                    create_directory(path)
                    with open(path+name, 'wb') as f:
                        f.write(pdf)
                        filecount += 1
        except (error.HTTPError, utils.PdfReadError) as e:
            if e.code == 404:
                logging.debug('File not found during requests to {0} : {1}'.format(_URL, str(e)))
            else:
                logging.debug('Error while reading from PDF object {0}: {1}'.format(name, str(e)))
                raise
    end = time.time()
    logging.info('Ticker: ' + str(_TICKER))
    logging.info('Execution Time: ' + str(round(end-start, 2)) + ' seconds')
    logging.info('Number of files copied over: ' + str(filecount) + " out of " + str(urlcount))
    logging.info('\n')


"""
Search for href links in a HTTP response object and store PDFs in a dictionary
"""
def scrape_pdf_links(url, domain, response, numberOfUrls):
    urls = []
    names = []

    if response is not None:
        response = BeautifulSoup(response, 'html.parser')
        for i, link in enumerate(response.findAll('a')):
            fullUrl = str(link.get('href'))
            linkType = str(link.get('type'))
            if 'pdf' in linkType or '.pdf' in fullUrl:
                if not str(fullUrl).startswith('http'):
                    fullUrl = domain + fullUrl
                urls.append(fullUrl)
                name = response.select('a')[i].attrs['href'].replace('/', '_')
                if '.com' in name:
                    name = name.split('.com')[1]
                if not name.endswith('.pdf'):
                    name = name + '.pdf'
                names.append(name)
                numberOfUrls += 1
        return zip(names, urls)
    else:
        # Raise an exception if we failed to get any data from the url
        logging.debug('Error found for {}'.format(response))
        raise Exception('Error retrieving contents at {}'.format(url))


"""
Handles missing EOF marker error
"""
def decompress_pdf(temp_buffer):
    temp_buffer.seek(0)  # Make sure we're at the start of the file.

    process = subprocess.Popen(['pdftk.exe',
                                '-',  # Read from stdin.
                                'output',
                                '-',  # Write to stdout.
                                'uncompress'],
                                stdin=temp_buffer,
                                stdout=subprocess.PIPE,
                                stderr=subprocess.PIPE)
    stdout, stderr = process.communicate()

    return io.StringIO(stdout)


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
            PDF_DIRECTORY = config["directory"]["target"]
            TEST_DIRECTORY = config["directory"]["testsource"]
        numberOfFiles = len([name for name in os.listdir(LOG_DIRECTORY)]);
        logging.basicConfig(filename=LOG_DIRECTORY+'Log_'+str(numberOfFiles)+'.log', filemode='w', level=logging.DEBUG)
        logging.getLogger().addHandler(logging.StreamHandler(sys.stdout))
        logging.info('Initiated scraping...')
        with open(TEST_DIRECTORY+'testData.json', 'r') as f:
            datastore = json.load(f)
        for index, company in enumerate(datastore):
            get_report(company)
    except FileNotFoundError as e:
        logging.debug('JSON file not found: {0}'.format(str(e)))
    finally:
        logging.info('Finished')



