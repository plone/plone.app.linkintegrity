# -*- coding: utf-8 -*-
from Acquisition import aq_inner
from OFS.interfaces import IFolder
from Products.CMFCore.permissions import AccessContentsInformation
from Products.CMFCore.utils import _checkPermission
from Products.CMFCore.utils import getToolByName
from Products.CMFPlone.interfaces.siteroot import IPloneSiteRoot
from Products.Five import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from plone.app.linkintegrity.utils import getIncomingLinks
from plone.app.linkintegrity.utils import linkintegrity_enabled
from plone.uuid.interfaces import IUUID
from zope.i18n import translate


class DeleteConfirmationInfo(BrowserView):

    template = ViewPageTemplateFile('delete_confirmation_info.pt')

    def __init__(self, context, request):
        self.linkintegrity_enabled = linkintegrity_enabled()
        self.context = context
        self.request = request

    def __call__(self, items=None):
        if not self.linkintegrity_enabled:
            return
        if items is None:
            if IPloneSiteRoot.providedBy(self.context):
                # Checking the portal for breaches makes no sense.
                return
            else:
                items = [self.context]
        self.breaches = self.get_breaches(items)
        return self.template()

    def get_breaches(self, items=None):
        """Return breaches for multiple items.

        Breaches coming from objects in the list of items
        or their children (if a object is a folder) will be ignored.
        """
        if items is None:

            items = [self.context]
        catalog = getToolByName(self.context, 'portal_catalog')
        results = []
        uids_to_ignore = []
        for obj in items:
            obj_path = '/'.join(obj.getPhysicalPath())
            brains_to_delete = catalog(path={'query': obj_path})
            # add the current items uid and all its childrens uids to the
            # list of uids that are ignored
            uids_to_ignore.extend([i.UID for i in brains_to_delete])
            for breach in self.get_breaches_for_item(obj):
                add_breach = False
                for source in breach['sources']:
                    # Only add the breach if one the sources is not in the
                    # list of items that are to be deleted.
                    if source['uid'] not in uids_to_ignore:
                        add_breach = True
                if add_breach:
                    results.append(breach)

        # Cleanup: Some breaches where added before it was known
        # that their source will be deleted too.
        for result in results:
            for source in result['sources']:
                if source['uid'] in uids_to_ignore:
                    # Drop sources that are also being deleted
                    result['sources'].remove(source)
                    if not result['sources']:
                        # Remove the breach is there are no more sources
                        # This check is necessary since there can be multiple
                        # sources for a breach
                        results.remove(result)
        return results

    def get_breaches_for_item(self, obj=None):
        """Get breaches for one object and its children.

        Breaches coming from the children of a folder are ignored by default.
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

        Breaches originating from excluded_path are ignored.
        """
        breaches = {}
        direct_links = getIncomingLinks(obj)
        has_breaches = False
        for direct_link in direct_links:
            source_path = direct_link.from_path
            if not source_path:
                # link is broken
                continue
            if excluded_path and source_path.startswith(excluded_path):
                # source is in excluded_path
                continue
            source = direct_link.from_object
            if not breaches.get('sources'):
                breaches['sources'] = []
            breaches['sources'].append({
                'uid': IUUID(source),
                'title': source.Title(),
                'url': source.absolute_url(),
                'accessible': self.is_accessible(source),
            })
            has_breaches = True
        if has_breaches:
            breaches['target'] = {
                'uid': IUUID(obj),
                'title': obj.Title(),
                'url': obj.absolute_url(),
                'portal_type': obj.portal_type,
                'type_title': self.get_portal_type_title(obj),
            }
            return breaches

    def get_portal_type_title(self, obj):
        """Get the portal type title of the object."""
        context = aq_inner(self.context)
        portal_types = getToolByName(context, 'portal_types')
        fti = portal_types.get(obj.portal_type)
        if fti is not None:
            type_title_msgid = fti.Title()
        else:
            type_title_msgid = obj.portal_type
        type_title = translate(type_title_msgid, context=self.request)
        return type_title

    def is_accessible(self, obj):
        return _checkPermission(AccessContentsInformation, obj)
