# -*- coding: utf-8 -*-
from six.moves.html_parser import HTMLParser

try:
    from html.parser import HTMLParseError
except ImportError as e:
    # HTMLParseError is removed in Python 3.5. Since it can never be
    # thrown in 3.5, we can just define our own class as a placeholder.
    class HTMLParseError(Exception):
        pass


class LinkParser(HTMLParser):
    """A simple html parser for link and image urls.
    """

    def __init__(self):
        HTMLParser.__init__(self)
        self.links = []

    def getLinks(self):
        """Return all links found during parsing.
        """
        return tuple(self.links)

    def handle_starttag(self, tag, attrs):
        """Override the method to remember all links.
        """
        if tag == 'a':
            self.links.extend(search_attr('href', attrs))
        if tag == 'img':
            self.links.extend(search_attr('src', attrs))


def search_attr(name, attrs):
    """Search named attribute in a list of attributes.
    """
    for attr, value in attrs:
        if attr == name:
            return [value]
    return []


def extractLinks(data, encoding='utf-8'):
    """Parse the given html and return all links.
    """
    if not data:
        return []
    parser = LinkParser()
    try:
        parser.feed(data)
        parser.close()
    except UnicodeDecodeError:
        parser = LinkParser()
        parser.feed(data.decode(encoding))
        parser.close()
    except (HTMLParseError, TypeError):
        pass

    return parser.getLinks()
