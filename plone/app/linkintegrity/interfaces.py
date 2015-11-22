from zope.interface import Interface

class IRetriever(Interface):
    """ A retriever for links in a content type """

    def retrieveLinks():
        """ retrieve links """
