# -*- coding: utf-8 -*-
from six.moves.html_parser import HTMLParser

try:
    from html.parser import HTMLParseError
except ImportError as e:
    # HTMLParseError is removed in Python 3.5. Since it can never be
    # thrown in 3.5, we can just define our own class as a placeholder.
    class HTMLParseError(Exception):
        pass


TAG_ATTRS_TO_TRACK = {
    # The humble hyperlink.
    "a": ["href"],
    # The image.
    "img": ["src", "srcset"],
    # Used within img/picture/audio/video tags
    # to embed various sources of media.
    "source": ["src", "srcset"],
    # Embeds audio recordings.
    "audio": ["src"],
    # Embeds videos.
    "video": ["src"],
    # Used to embed PDFs.
    "iframe": ["src"],
}


class LinkParser(HTMLParser):
    """A simple html parser for link and image urls."""

    def __init__(self):
        HTMLParser.__init__(self)
        self.links = []

    def getLinks(self):
        """Return all links found during parsing."""
        return tuple(self.links)

    def handle_starttag(self, tag, attrs):
        """Override the method to remember all links."""
        for at in TAG_ATTRS_TO_TRACK.get(tag.lower(), []):
            self.links.extend(search_attr(at, attrs))


def links_in_srcset(attrval):
    # SRCSET is split by commas, and each line's first
    # element is the URL in question.
    # Yes, this means that spaces in such a link must be
    # encoded with %20 or +.  That is what the written
    # standard implies.
    return [src.strip().split()[0] for src in attrval.split(",")]


def search_attr(name, attrs):
    """Search named attribute in a list of attributes."""
    for attr, value in attrs:
        if attr == name:
            return links_in_srcset(value) if name == "srcset" else [value]
    return []


def extractLinks(data, encoding="utf-8"):
    """Parse the given html and return all links."""
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
