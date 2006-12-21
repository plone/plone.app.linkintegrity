from Products.Five import BrowserView
from Products.CMFCore.utils import getToolByName
from plone.app.linkintegrity.interfaces import ILinkIntegrityInfo
from plone.app.linkintegrity.utils import encode


class RemoveConfirmationView(BrowserView):
    
    def __init__(self, context, request):
        # since this is a view adapting an exception and a request (instead
        # of a regular content object and a request), the exception object
        # was passed as the context;  therefore we need to construct a
        # proper context in order to render the template in a sane manner;
        # to do this we will assume that the desired context was passed as
        # the first exception value...
        self.exception = context
        self.context, = context.args
        self.request = request
    
    def originalRequest(self):
        # in order to interrupt the current request with a confirmation
        # question about removing the referred to object we need to save
        # the original request to be able to possibly continue it later on,
        # so we pickle and encode its body and environment...
        self.request.stdin.seek(0)
        
        # unfortunately on top of all that now we have to work around a bug
        # in ZopeTestCase:  in zopedoctest's function `http()` (in
        # Testing/ZopeTestCase/zopedoctest/functional.py:113) the passed in
        # request_string is used as stdin for `publish_module` (line 177),
        # but still contains http headers;  it doesn't matter normally,
        # because the headers are read when it is parsed as a rfc822 message
        # (line 164), so later in `processInputs()` (HTTPRequest.py:357) the
        # stream isn't read from its beginning and only the remaining request
        # body is parsed by the `FieldStorage` (HTTPRequest.py:389);  however,
        # when a Retry exception is raised, the stream is reset to its start
        # (HTTPRequest.py:133), so this time `processInputs()` gets all the
        # headers, including 'content-length';  this causes 'FieldStorage' to
        # only read the number of bytes as specified by 'content-length' from
        # the stream in `read_urlencoded()`;  since the stream contains the
        # headers, it is much longer than just the given length of the body
        # and therefore cut off...
        # to work around this (until it's fixed upstream) stdin is parsed
        # here using rfc822.Message (just like in `http()`) and only the
        # actual request body is stored for setting up the Retry later on...
        from rfc822 import Message
        dummy = Message(self.request.stdin)     # eat up the headers
        body = self.request.stdin.read()        # read the remainder...
        return encode((body, self.request._orig_env))
    
    def integrityBreaches(self):
        info = ILinkIntegrityInfo(self.request).getIntegrityInfo()
        breaches = []
        for target, sources in info.items():
            breaches.append({
                'title': target.Title(),
                'type': target.getPortalTypeName(),
                'url': target.absolute_url(),
                'sources': sources,
            })
        return breaches
    
    def confirmedItems(self):
        info = ILinkIntegrityInfo(self.request)
        targets = info.getIntegrityInfo().keys()
        return info.encodeConfirmedItems(additions=targets)
    
    def callbackURL(self):
        portal = getToolByName(self.context, 'portal_url')
        return portal() + '/removeConfirmationAction'
    
    def cancelURL(self):
        url = self.request.environ.get('HTTP_REFERER', None)
        if url is None:
            url = getToolByName(self.context, 'portal_url')()
        return url
    

