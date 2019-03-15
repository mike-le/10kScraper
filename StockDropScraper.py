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


def get_report():
    """
    Downloads the PDFs from the given url
    """
    urls = []
    names = []
    #_URL = "https://ir.aboutamazon.com/sec-filings?field_nir_sec_form_group_target_id%5B%5D=471&field_nir_sec_date_filed_value=&items_per_page=10"
    _DOMAIN = "https://abc.xyz/"
    _URL = _DOMAIN + "investor"
    response = simple_get(_URL)

    if response is not None:
        response = BeautifulSoup(response, 'html.parser')
        
        for i, link in enumerate(response.findAll('a')):
            _FULLURL = str(link.get('href'))
            _TYPE = str(link.get('type'))
            if ('pdf' in _TYPE or '.pdf' in _FULLURL) and '10K' in _FULLURL:
                urls.append(_DOMAIN + _FULLURL)
                name = response.select('a')[i].attrs['href'].replace('/', '_')
                if not name.endswith('.pdf'):
                    name = name + '.pdf'
                names.append(name)
        names_urls = zip(names, urls)

        numberOfFiles = 0
        for name, url in names_urls:
            try:
                rq = urllib.request.urlopen(url)
                header = rq.info()
                if 'Content-Disposition' in str(header) or 'application/pdf' in str(header):
                    with open(name, 'wb') as f:
                        f.write(rq.read())
                        numberOfFiles += 1
            except RequestException as e:
                log_error('Error during requests to {0} : {1}'.format(_URL, str(e)))
        print('Number of files copied over: ' + str(numberOfFiles))
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



