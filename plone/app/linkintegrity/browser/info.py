# -*- coding: utf-8 -*-
from Acquisition import aq_inner
from OFS.interfaces import IFolder
from Products.CMFCore.permissions import AccessContentsInformation
from Products.CMFCore.utils import getToolByName, _checkPermission
from Products.CMFPlone.interfaces import IEditingSchema
from Products.Five import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from plone.app.linkintegrity.utils import getIncomingLinks
from plone.registry.interfaces import IRegistry
from zope.component import getUtility
from zope.i18n import translate


class DeleteConfirmationInfo(BrowserView):

    template = ViewPageTemplateFile('delete_confirmation_info.pt')

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

    def shallowCheckObject(self, obj):
        result = []
        for element in getIncomingLinks(obj):
            result.append(element.from_object)

        if len(result):
            return {
                'title': obj.Title(),
                'url': obj.absolute_url(),
                'sources': result,
                'type': obj.getPortalTypeName(),
                'type_title': self.getPortalTypeTitle(obj)
            }

    def checkObject(self, obj):
        if not hasattr(self, 'breaches'):
            self.breaches = []
        check = self.shallowCheckObject(obj)
        if check:
            self.breaches.append(check)

        if IFolder.providedBy(obj):
            # now check if folder and go through children
            # looking for links....
            # Unfortunately, there doesn't seem to be a better,
            # less expensive way to do this. This operation could
            # potentially cost a lot of cycles...
            catalog = getToolByName(self.context, 'portal_catalog')
            folder_path = '/'.join(obj.getPhysicalPath())
            for brain in catalog(path={'query': folder_path}):
                ob = brain.getObject()
                check = self.shallowCheckObject(ob)
                if check:
                    self.breaches.append(check)

    def linkintegrity_enabled(self):
        reg = getUtility(IRegistry)
        editing_settings = reg.forInterface(IEditingSchema, prefix='plone')
        return editing_settings.enable_link_integrity_checks

    def __call__(self, skip_context=False):
        if not self.linkintegrity_enabled():
            self.breaches = []
        elif not skip_context:
            self.checkObject(self.context)
        return self.template()
