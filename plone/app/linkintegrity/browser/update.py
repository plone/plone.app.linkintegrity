from Acquisition import aq_inner
from Products.Archetypes.interfaces import IBaseObject
from Products.CMFCore.utils import getToolByName
from Products.CMFPlone import PloneMessageFactory as _
from Products.Five import BrowserView
from Products.statusmessages.interfaces import IStatusMessage
from plone.app.linkintegrity.handlers import modifiedArchetype


class UpdateView(BrowserView):

    def __call__(self):
        context = aq_inner(self.context)
        request = aq_inner(self.request)
        clicked = request.form.has_key
        if clicked('update') or clicked('delete_all'):
            count = self.update()
            msg = _(u'linkintegrity_update_info',
                default=u'Link integrity information updated for ${count} item(s).',
                mapping={'count': count})
            IStatusMessage(request).addStatusMessage(msg, type='info')
            request.RESPONSE.redirect(getToolByName(context, 'portal_url')())
        elif clicked('cancel'):
            msg = _(u'Update cancelled.')
            IStatusMessage(request).addStatusMessage(msg, type='info')
            request.RESPONSE.redirect(getToolByName(context, 'portal_url')())
        else:
            return self.index()

    def update(self):
        catalog = getToolByName(self.context, 'portal_catalog')
        count = 0
        for brain in catalog(Language='all'):
            obj = brain.getObject()
            if IBaseObject.providedBy(obj):
                modifiedArchetype(obj, 'dummy event parameter')
                count += 1
        return count
