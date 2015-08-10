# -*- coding: utf-8 -*-
from Acquisition import aq_inner
from OFS.interfaces import IFolder
from Products.CMFCore.permissions import AccessContentsInformation
from Products.CMFCore.utils import getToolByName, _checkPermission
from Products.Five import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from collections import defaultdict
from plone.app.linkintegrity.utils import getIncomingLinks
from plone.app.linkintegrity.utils import linkintegrity_enabled
from plone.uuid.interfaces import IUUID
from zope.i18n import translate


class DeleteConfirmationInfo(BrowserView):

    template = ViewPageTemplateFile('delete_confirmation_info.pt')

    def __call__(self):
        self.linkintegrity_enabled = linkintegrity_enabled()
        return self.template()

    def get_breaches_for_items(self, items):
        """Check for breaches when deleting multiple items at once.
        Breaches originating from items that will also be deleted are dropped.
        """
        catalog = getToolByName(self.context, 'portal_catalog')
        results = []
        uids_to_delete = []
        for obj in items:
            obj_path = '/'.join(obj.getPhysicalPath())
            brains_to_delete = catalog(path={'query': obj_path})
            uids_to_delete.extend([i.UID for i in brains_to_delete])
            for breach in self.get_breaches(obj):
                add_breach = False
                for source in breach['sources']:
                    if source['uid'] not in uids_to_delete:
                        add_breach = True
                if add_breach:
                    results.append(breach)

        # cleanup (some breaches where added before it was clear
        # that the source will be deleted too)
        for result in results:
            for source in result['sources']:
                if source['uid'] in uids_to_delete:
                    result['sources'].remove(source)
                    if not result['sources']:
                        results.remove(result)
        return results

    def get_breaches(self, obj=None):
        """Check one object and it's children for breaches.
        """
        if obj is None:
            obj = self.context
        results = []
        catalog = getToolByName(obj, 'portal_catalog')
        obj_path = '/'.join(obj.getPhysicalPath())

        breaches = self.check_object(obj)
        if breaches:
            results.append(breaches)

        if IFolder.providedBy(obj):
            brains = catalog(path={'query': obj_path})
            for brain in brains:
                child = brain.getObject()
                if child == obj:
                    continue
                breaches = self.check_object(obj=child, excluded_path=obj_path)
                if breaches:
                    results.append(breaches)
        self.breaches = results
        return results

    def check_object(self, obj, excluded_path=None):
        """Check one object for breaches.
        If breaches origin from excluded_path ignore them
        """
        if excluded_path is None:
            excluded_path = '/'.join(obj.getPhysicalPath())
        breaches = defaultdict(list)
        direct_links = getIncomingLinks(obj)
        has_breaches = False
        for direct_link in direct_links:
            source_path = direct_link.from_path
            if not source_path or source_path.startswith(excluded_path):
                # broken or child of item that is to be deleted
                continue
            source = direct_link.from_object
            breaches['sources'].append({
                'uid': IUUID(source),
                'title': source.Title(),
                'url': source.absolute_url(),
                'accessible': self.isAccessible(source),
            })
            has_breaches = True
        if has_breaches:
            breaches['target'] = {
                'uid': IUUID(obj),
                'title': obj.Title(),
                'url': obj.absolute_url(),
                'portal_type': obj.portal_type,
                'type_title': self.getPortalTypeTitle(obj),
            }
        if has_breaches:
            return breaches

    def getPortalTypeTitle(self, obj):
        # Get the portal type title of the object.
        context = aq_inner(self.context)
        portal_types = getToolByName(context, 'portal_types')
        fti = portal_types.get(obj.portal_type)
        if fti is not None:
            type_title_msgid = fti.Title()
        else:
            type_title_msgid = obj.portal_type
        type_title = translate(type_title_msgid, context=self.request)
        return type_title

    def isAccessible(self, obj):
        return _checkPermission(AccessContentsInformation, obj)
