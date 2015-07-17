# -*- coding: utf-8 -*-
from Acquisition import aq_inner
from Products.Five import BrowserView
from Products.CMFCore.utils import getToolByName, _checkPermission
from Products.CMFCore.permissions import AccessContentsInformation
from plone.app.linkintegrity.utils import encodeRequestData
from zope.component import getMultiAdapter
from zope.i18n import translate
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from plone.app.linkintegrity.utils import isLinked


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

    def integrityBreaches(self):
        result = []
        for element in isLinked(self.context):
            result.append(element.from_object)

        if len(result):
            return [{
                'title': self.context.Title(),
                'url': self.context.absolute_url(),
                'sources': result,
                'type': self.context.getPortalTypeName(),
                'type_title': self.getPortalTypeTitle(self.context)
            }]
        else:
            return []

    def __call__(self):
        return self.template()
