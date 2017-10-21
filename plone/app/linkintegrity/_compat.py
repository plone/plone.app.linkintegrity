# coding=utf-8
import sys


PY3 = sys.version_info[0] == 3
if PY3:
    from io import StringIO
    from html.parser import HTMLParseError
    from html.parser import HTMLParser
    from urllib.parse import urlsplit
else:
    from HTMLParser import HTMLParseError  # noqa
    from HTMLParser import HTMLParser  # noqa
    from StringIO import StringIO  # noqa
    from urlparse import urlsplit  # noqa
