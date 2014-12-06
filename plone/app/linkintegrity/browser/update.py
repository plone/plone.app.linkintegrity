# -*- coding: utf-8 -*-
from Acquisition import aq_inner
from Products.Archetypes.interfaces import IBaseObject
from Products.CMFCore.utils import getToolByName
from Products.CMFPlone import PloneMessageFactory as _
from Products.Five import BrowserView
from Products.statusmessages.interfaces import IStatusMessage

from plone.app.linkintegrity.handlers import modifiedArchetype
from plone.app.linkintegrity.handlers import modifiedDexterity
from plone.app.linkintegrity import HAS_LINGUAPLONE
from plone.app.linkintegrity import HAS_PAM
from plone.app.referenceablebehavior.referenceable import IReferenceable
from plone.dexterity.interfaces import IDexterityContent


class UpdateView(BrowserView):

    def __call__(self):
        context = aq_inner(self.context)
        request = aq_inner(self.request)
        clicked = request.form.has_key
        if clicked('update') or clicked('delete_all'):
            count = self.update()
            msg = _(
                u'linkintegrity_update_info',
                default=u'Link integrity information updated for ${count} ' +
                        u'item(s).',
                mapping={'count': count},
            )
            IStatusMessage(request).add(msg, type='info')
            request.RESPONSE.redirect(getToolByName(context, 'portal_url')())
        elif clicked('cancel'):
            msg = _(u'Update cancelled.')
            IStatusMessage(request).add(msg, type='info')
            request.RESPONSE.redirect(getToolByName(context, 'portal_url')())
        else:
            return self.index()

    def update(self):
        catalog = getToolByName(self.context, 'portal_catalog')
        count = 0
        kwargs = {}

        if HAS_LINGUAPLONE or HAS_PAM:
            kwargs['Language'] = 'all'

        for brain in catalog(**kwargs):
            obj = brain.getObject()
            if IBaseObject.providedBy(obj):
                modifiedArchetype(obj, 'dummy event parameter')
                count += 1
            elif IDexterityContent.providedBy(obj):
                if IReferenceable.providedBy(obj):
                    modifiedDexterity(obj, 'dummy event parameter')
                count += 1
        return count
