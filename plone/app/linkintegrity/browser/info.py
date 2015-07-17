# -*- coding: utf-8 -*-
from Acquisition import aq_inner
from Products.CMFCore.permissions import AccessContentsInformation
from Products.CMFCore.utils import getToolByName, _checkPermission
from Products.Five import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from plone.app.linkintegrity.utils import getIncomingLinks
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

    def checkObject(self, obj):
        if not hasattr(self, 'breaches'):
            self.breaches = []
        result = []
        for element in getIncomingLinks(obj):
            result.append(element.from_object)

        if len(result):
            self.breaches.append({
                'title': obj.Title(),
                'url': obj.absolute_url(),
                'sources': result,
                'type': obj.getPortalTypeName(),
                'type_title': self.getPortalTypeTitle(obj)
            })

    def __call__(self, skip_context=False):
        if not skip_context:
            self.checkObject(self.context)
        return self.template()
