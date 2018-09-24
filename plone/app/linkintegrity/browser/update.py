# -*- coding: utf-8 -*-
from Acquisition import aq_inner
from Products.Archetypes.interfaces import IBaseObject
from Products.Archetypes.interfaces import IReferenceable
from Products.CMFCore.utils import getToolByName
from Products.CMFPlone import PloneMessageFactory as _
from Products.Five import BrowserView
from Products.statusmessages.interfaces import IStatusMessage
from datetime import datetime
from datetime import timedelta
from plone.app.linkintegrity.handlers import modifiedArchetype
from plone.app.linkintegrity.handlers import modifiedDexterity
from zExceptions import NotFound
import logging
import pkg_resources

try:
    pkg_resources.get_distribution('plone.dexterity')
except pkg_resources.DistributionNotFound:
    HAS_DEXTERITY = False
else:
    HAS_DEXTERITY = True
    from plone.dexterity.interfaces import IDexterityContent

# Is there a multilingual addon?
try:
    pkg_resources.get_distribution('Products.LinguaPlone')
except pkg_resources.DistributionNotFound:
    HAS_MULTILINGUAL = False
else:
    HAS_MULTILINGUAL = True
    ALL_QUERY_MULTILINGUAL = {'Language': 'all'}

if not HAS_MULTILINGUAL:
    try:
        pkg_resources.get_distribution('plone.app.multilingual')
    except pkg_resources.DistributionNotFound:
        HAS_MULTILINGUAL = False
    else:
        HAS_MULTILINGUAL = True
        try:
            from plone.app.multilingual.upgrades import migration_pam_1_to_2
        except ImportError:
            ALL_QUERY_MULTILINGUAL = {'Language': 'all'}
        else:
            ALL_QUERY_MULTILINGUAL = {'path': '/'}

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
                        u'items in ${time} seconds.',
                mapping={'count': count, 'time': str(duration)},
            )
            IStatusMessage(request).add(msg, type='info')
            msg = 'Updated {0} items in {1} seconds'.format(count, str(duration))
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

        # test if multilingual is indeed installed in the site (not only as a module)
        if HAS_MULTILINGUAL and 'Language' in catalog.indexes():
            all_content_query = ALL_QUERY_MULTILINGUAL
        else:
            all_content_query = {}

        for brain in catalog(all_content_query):
            try:
                obj = brain.getObject()
            except (AttributeError, NotFound, KeyError):
                msg = "Catalog inconsistency: {} not found!"
                logger.error(msg.format(brain.getPath()), exc_info=1)
                continue
            method = None
            if IBaseObject.providedBy(obj):
                method = modifiedArchetype
            elif HAS_DEXTERITY and IDexterityContent.providedBy(obj):
                try:
                    IReferenceable(obj)
                except TypeError:
                    method = None
                else:
                    method = modifiedDexterity
            if method:
                try:
                    method(obj, 'dummy event parameter')
                    count += 1
                except Exception:
                    msg = "Error updating linkintegrity-info for {}."
                    logger.error(msg.format(obj.absolute_url()), exc_info=1)
        return count
