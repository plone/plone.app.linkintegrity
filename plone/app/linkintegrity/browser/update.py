# -*- coding: utf-8 -*-
from Acquisition import aq_inner
from Products.Archetypes.interfaces import IBaseObject
from Products.CMFCore.utils import getToolByName
from Products.CMFPlone import PloneMessageFactory as _
from Products.Five import BrowserView
from Products.statusmessages.interfaces import IStatusMessage
from datetime import datetime
from datetime import timedelta
from plone.app.linkintegrity.handlers import modifiedArchetype
from plone.app.linkintegrity.handlers import modifiedDexterity
from plone.dexterity.interfaces import IDexterityContent
from zExceptions import NotFound
import logging
import traceback

logger = logging.getLogger(__name__)


class UpdateView(BrowserView):

    def __call__(self):
        context = aq_inner(self.context)
        request = aq_inner(self.request)
        clicked = request.form.has_key
        if clicked('update') or clicked('delete_all'):
            starttime = datetime.now()
            count = self.update()
            duration = timedelta(seconds=(datetime.now() - starttime).seconds)
            msg = _(
                u'linkintegrity_update_info',
                default=u'Link integrity information updated for ${count} ' +
                        u'items in {time} seconds.',
                mapping={'count': count, 'time': str(duration)},
            )
            IStatusMessage(request).add(msg, type='info')
            msg = 'Updated {} items in {} seconds'.format(count, str(duration))
            logger.info(msg)
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

        for brain in catalog(**kwargs):
            try:
                obj = brain.getObject()
            except (AttributeError, NotFound, KeyError), e:
                trace = traceback.format_exc()
                msg = "Catalog inconsistency: {0} not found!: \n{1}\n{2}\n"
                logger.error(msg.format(brain.getPath(), e, trace))
            if IBaseObject.providedBy(obj):
                modifiedArchetype(obj, 'dummy event parameter')
                count += 1
            elif IDexterityContent.providedBy(obj):
                modifiedDexterity(obj, 'dummy event parameter')
                count += 1
        return count
