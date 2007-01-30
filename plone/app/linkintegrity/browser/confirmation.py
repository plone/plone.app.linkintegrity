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
        body = self.request.stdin.getvalue()    # zope2 request body...
        return encode((body, self.request._orig_env))
    
    def integrityBreaches(self):
        info = ILinkIntegrityInfo(self.request).getIntegrityBreaches()
        breaches = []
        for target, sources in info.items():
            breaches.append({
                'title': target.Title(),
                'type': target.getPortalTypeName(),
                'url': target.absolute_url(),
                'sources': sources,
            })
        return sorted(breaches, lambda a,b: cmp(a['title'], b['title']))
    
    def confirmedItems(self):
        info = ILinkIntegrityInfo(self.request)
        targets = info.getIntegrityBreaches().keys()
        return info.encodeConfirmedItems(additions=targets)
    
    def callbackURL(self):
        portal = getToolByName(self.context, 'portal_url')
        return portal() + '/removeConfirmationAction'
    
    def cancelURL(self):
        url = self.request.environ.get('HTTP_REFERER', None)
        if url is None:
            url = getToolByName(self.context, 'portal_url')()
        return url
    

