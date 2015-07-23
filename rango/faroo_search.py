import os
import urllib
import requests


def get_key(filename):
    """
    Reads API key from file.
    """
    try:
        with open(filename, 'r') as f:
            key = f.read()
    except IOError as err:
        print(err)
    else:
        return key.rstrip()


def sanitize(search_terms):
    """
    Remove characters which are not allowed within the query /=():;
    Resolve spaces within `search_terms`.
    """
    res = ''

    # Remove /=():;
    for ch in search_terms:
        if ch not in '/=():;':
            res += ch

    # Resolve spaces.
    return urllib.quote(res)


def compose_params(params_dict):
    """
    Compose key - value pairs for URL from the given dict.
    """
    lst = []
    for k, v in params_dict.items():
        lst.append(k + '=' + v)

    return '&'.join(lst)


def run_query(search_terms, api_key):
    # Base.
    root_url = 'http://www.faroo.com/'
    source = 'api'
    query = sanitize(search_terms)

    # Construct request URL.
    params = {'start':  '1',            # Start (default=1)
              'length': '10',           # Length (default=10; maximum=10)
              'l':      'en',           # Language; en-English (default)
              'src':    'web',          # Source; web-Web Search
              'i':      'false',        # Instant search; false - searches for query q
              'f':      'json',         # Result format
              'key':    api_key}

    search_url = "{0}{1}?q={2}&{3}".format(root_url,
                                           source,
                                           query,
                                           compose_params(params))

    # GET and fetch JSON.
    try:
        # `params` is not used since it's incorrectly encodes API key.
        r = requests.get(search_url)

    except (requests.ConnectionError,
            requests.HTTPError,
            requests.Timeout,
            requests.TooManyRedirects) as err:
        print(err)

    else:
        return r.json()


#
# Get API key.
#
dir_path = os.path.dirname(__file__)
file_path = os.path.join(dir_path, 'api_key.txt')
API_KEY = get_key(file_path)
