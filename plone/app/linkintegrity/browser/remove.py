from Acquisition import aq_inner
from base64 import b64encode
from StringIO import StringIO
from ZPublisher.Publish import Retry

from Products.CMFPlone import PloneMessageFactory as _
from Products.Five import BrowserView
from Products.statusmessages.interfaces import IStatusMessage

from plone.app.linkintegrity.interfaces import ILinkIntegrityInfo
from plone.app.linkintegrity.utils import decodeRequestData


class RemoveReferencedObjectView(BrowserView):

    def __init__(self, context, request):
        self.context = context
        self.request = request

    def __call__(self):
        # this view is intended to provide an action called by the
        # confirmation form;  all it does is prepare the request for
        # the retry exception and raise it...
        context = aq_inner(self.context)
        request = aq_inner(self.request)
        clicked = request.form.has_key
        if clicked('delete') or clicked('delete_all'):
            # the user choose to actually delete the referred to object,
            # so we reconstruct the original request which we interrupted
            # before, store the so far confirmed items and retry it...
            body, env = decodeRequestData(request.get('original_request'))
            marker = ILinkIntegrityInfo(request).getEnvMarker()
            if clicked('delete_all'):
                env[marker] = 'all'
            else:
                env[marker] = request.get('confirmed_items')
            auth = request._authUserPW()
            if auth is not None:
                authtoken = b64encode('%s:%s' % auth)
                env['HTTP_AUTHORIZATION'] = 'Basic %s' % authtoken
            env['HTTP_COOKIE'] = request.get('HTTP_COOKIE', '')
            setattr(request, 'stdin', StringIO(body))
            setattr(request, '_orig_env', env)
            raise Retry
        else:
            # the user choose to cancel the removal, in which case we
            # redirect back to the original HTTP_REFERER url...
            msg = _(u'Removal cancelled.')
            IStatusMessage(request).addStatusMessage(msg, type='info')
            request.RESPONSE.redirect(request.get('cancel_url'))

