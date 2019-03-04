from requests import get
from requests.exceptions import RequestException
from contextlib import closing
from bs4 import BeautifulSoup
import urllib
from urllib import request


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


def get_names():
    """
    Downloads the page where the list of mathematicians is found
    and returns a list of strings, one per mathematician
    """
    url = 'http://www.fabpedigree.com/james/mathmen.htm'
    response = simple_get(url)

    if response is not None:
        html = BeautifulSoup(response, 'html.parser')
        names = set()
        for li in html.select('li'):
            for name in li.text.split('\n'):
                if len(name) > 0:
                    names.add(name.strip())
        return list(names)

    # Raise an exception if we failed to get any data from the url
    raise Exception('Error retrieving contents at {}'.format(url))


def get_report():
    """
    Downloads the PDFs from the given url
    """
    urls = []
    names = []
    _URL = "https://ir.aboutamazon.com/sec-filings?field_nir_sec_form_group_target_id%5B%5D=471&field_nir_sec_date_filed_value=&items_per_page=10"
    response = simple_get(_URL)

    if response is not None:
        response = BeautifulSoup(response, 'html.parser')
        
        for i, link in enumerate(response.findAll('a')):
            _FULLURL = str(link.get('href'))
            _TYPE = str(link.get('type'))
            if 'pdf' in _TYPE:
                urls.append(_FULLURL)
                names.append(response.select('a')[i].attrs['href'])
        names_urls = zip(names, urls)

        for name, url in names_urls:
            print(url)
            rq = urllib.request.urlopen(url)
            with open('/pdfs', 'wb') as f:
                f.write(rq.read())
    else:
        # Raise an exception if we failed to get any data from the url
        log_error('error found for {}'.format(response))
        raise Exception('Error retrieving contents at {}'.format(_URL))


def is_good_response(resp):
    content_type = resp.headers['Content-Type'].lower()
    return (resp.status_code == 200
            and content_type is not None
            and content_type.find('html') > -1)


def log_error(e):
    print(e)


get_report()


