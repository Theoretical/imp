"""
    
    ~~~
    
    By: Alex on 9/20/2015
"""
import requests

__author__ = 'Alex'

import re
import sys
import urllib

from html.entities import name2codepoint
from urllib.parse import urlparse
from urllib.parse import urlunparse
unichr = chr

try:
    import ssl
    if not hasattr(ssl, 'match_hostname'):
        # Attempt to import ssl_match_hostname from python-backports
        import backports.ssl_match_hostname
        ssl.match_hostname = backports.ssl_match_hostname.match_hostname
        ssl.CertificateError = backports.ssl_match_hostname.CertificateError
    has_ssl = True
except ImportError:
    has_ssl = False


# HTTP GET
# Note: dont_decode is a horrible name for an argument, double negative
# is super confusing. We need to replace it, maybe in 5.0 because this would
# mean breaking backwards compatability
def get(uri, timeout=20, headers=None, return_headers=False, limit_bytes=None):
    if not uri.startswith('http'):
        uri = "http://" + uri
    u = requests.get(uri, headers=headers, timeout=timeout)
    bytes = u.text
    headers = u.headers
    if not return_headers:
        return bytes
    else:
        headers['_http_status'] = u.status_code
        return (bytes, headers)


# Get HTTP headers
def head(uri, timeout=20, headers=None, verify_ssl=True):
    """Execute an HTTP GET query on `uri`, and return the headers.
    `timeout` is an optional argument, which represents how much time we should
    wait before throwing a timeout exception. It defaults to 20, but can be set
    to higher values if you are communicating with a slow web application.
    """
    if not uri.startswith('http'):
        uri = "http://" + uri
    u = requests.head(uri, timeout=20, headers=headers, verify_ssl=verify_ssl)
    info = u.headers
    return info


# HTTP POST
def post(uri, query, limit_bytes=None, timeout=20, verify_ssl=True, return_headers=False):
    """Execute an HTTP POST query.
    `uri` is the target URI, and `query` is the POST data. `headers` is a dict
    of HTTP headers to send with the request.
    If `limit_bytes` is provided, only read that many bytes from the URL. This
    may be a good idea when reading from unknown sites, to prevent excessively
    large files from being downloaded.
    """
    if not uri.startswith('http'):
        uri = "http://" + uri
    u = requests.post(uri, timeout=timeout, data=query)
    bytes = u.text
    headers = u.headers
    if not return_headers:
        return bytes
    else:
        headers['_http_status'] = u.status_code
        return (bytes, headers)

r_entity = re.compile(r'&([^;\s]+);')


def entity(match):
    value = match.group(1).lower()
    if value.startswith('#x'):
        return unichr(int(value[2:], 16))
    elif value.startswith('#'):
        return unichr(int(value[1:]))
    elif value in name2codepoint:
        return unichr(name2codepoint[value])
    return '[' + value + ']'


def decode(html):
    return r_entity.sub(entity, html)


# Identical to urllib2.quote
def quote(string, safe='/'):
    """Like urllib2.quote but handles unicode properly."""
    return urllib.parse.quote(str(string), safe)

def quote_query(string):
    """Quotes the query parameters."""
    parsed = urlparse(string)
    string = string.replace(parsed.query, quote(parsed.query, "/=&"), 1)
    return string


# Functions for international domain name magic

def urlencode_non_ascii(b):
    regex = '[\x80-\xFF]'
    if sys.version_info.major > 2:
        regex = b'[\x80-\xFF]'
    return re.sub(regex, lambda c: '%%%02x' % ord(c.group(0)), b)


def iri_to_uri(iri):
    parts = urlparse(iri)
    parts_seq = (part.encode('idna') if parti == 1 else urlencode_non_ascii(part.encode('utf-8')) for parti, part in enumerate(parts))
    if sys.version_info.major > 2:
        parts_seq = list(parts_seq)

    parsed = urlunparse(parts_seq)
    if sys.version_info.major > 2:
        return parsed.decode()
    else:
        return parsed