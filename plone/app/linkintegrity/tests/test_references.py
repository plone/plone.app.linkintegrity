# -*- coding: utf-8 -*-
from zope.event import notify
from zope.lifecycleevent import ObjectModifiedEvent
from Products.Archetypes.interfaces import IReferenceable as IATReferenceable
from plone.app.referenceablebehavior.referenceable import IReferenceable

from plone.app.testing import setRoles
from plone.app.testing import logout
from plone.app.testing import login
from plone.app.testing import TEST_USER_ID
from plone.app.testing import TEST_USER_NAME
from plone.app.testing import TEST_USER_PASSWORD
from plone.app.textfield import RichTextValue
from plone.app.linkintegrity.parser import extractLinks
from plone.app.linkintegrity.testing import (
    PLONE_APP_LINKINTEGRITY_AT_INTEGRATION_TESTING,
    PLONE_APP_LINKINTEGRITY_DX_INTEGRATION_TESTING
)
from plone.testing.z2 import Browser
from zope.lifecycleevent import modified

import transaction
import unittest

from plone.app.linkintegrity import exceptions


class ReferenceGenerationDXTests(unittest.TestCase):

    layer = PLONE_APP_LINKINTEGRITY_DX_INTEGRATION_TESTING
    reference_interface = IReferenceable

    def setUp(self):
        self.portal = self.layer['portal']
        self.request = self.layer['request']

        # Get a testbrowser
        self.browser = Browser(self.layer['app'])
        self.browser.handleErrors = False
        self.browser.addHeader(
            'Authorization',
            'Basic {0:s}:{1:s}'.format(TEST_USER_NAME, TEST_USER_PASSWORD))

        setRoles(self.portal, TEST_USER_ID, ['Manager', ])

    def _set_text(self, obj, text):
        setattr(obj, 'text', RichTextValue(text))
        modified(obj)
        transaction.commit()

    def _get_text(self, obj):
        return getattr(obj, 'text')

    def test_notification_exception(self):
        self.setText(self.portal['doc3'], '<a href="doc1">doc1</a>')
        self.assertRaises(
            exceptions.LinkIntegrityNotificationException,
            self.portal.manage_delObjects, ['doc1'])

    def test_circular_reference_deletion(self):
        login(self.portal, TEST_USER_NAME)
        doc1 = self.portal['doc1']
        doc2 = self.portal['doc2']
        doc3 = self.portal['doc3']
        self.setText(doc1, '<a href="doc2">doc2</a>')
        self.setText(doc2, '<a href="doc3">doc3</a>')
        self.setText(doc3, '<a href="doc1">doc1</a>')
        self.portal.manage_delObjects(
            ['doc1', 'doc2', 'doc3'], self.request)
        self.assertTrue('doc1' not in self.portal)
        self.assertTrue('doc2' not in self.portal)
        self.assertTrue('doc3' not in self.portal)

    def test_is_linked(self):
        from Products.CMFPlone.utils import isLinked
        img1 = self.portal['image1']
        doc1 = self.portal['doc1']
        self.setText(doc1, '<img src="image1"></img>')
        self.assertTrue(isLinked(img1))

    def testReferencesToNonAccessibleContentAreGenerated(self):
        setRoles(self.portal, TEST_USER_ID, ['Manager'])
        secret = self.portal[self.portal.invokeFactory('Document', id='secret')]
#        from_member = self.portal[self.portal.invokeFactory('Document',
#                                                            id='member')]
        from plone.dexterity.utils import createContentInContainer
        from_member = createContentInContainer(self.portal, 'Document', title=u"From Member")
        from_member.manage_setLocalRoles('member', ['Contributor'])
        # somebody created a document to which the user has no access...
        checkPermission = self.portal.portal_membership.checkPermission
        logout()
        login(self.portal, 'member')
        self.assertFalse(checkPermission('View', secret))
        self.assertFalse(checkPermission('Access contents information', secret))

    def test_link_extraction_easy(self):
        doc1 = self.portal.doc1
        self._set_text(doc1, '<a href="doc2">Doc 2</a>')
        self.assertEqual(
            extractLinks(self._get_text(doc1)),
            ('http://nohost/plone/doc2', )
        )

        # nevertheless it should be possible to set a link to it...
        from_member.text = '<html><body><a href="%s">go!</a></body></html>'\
            % secret.absolute_url()
        notify(ObjectModifiedEvent(from_member))
        self.assertEqual(IReferenceable(from_member).getReferences(), [secret])

    def test_link_extraction_more_complex(self):
        doc2 = self.portal.doc2
        self._set_text(
            doc2,
            '<a href="doc1">Doc 2</a>' +
            '<a href="folder1/doc3"><img src="image1" /></a>',
        )
        self.assertEqual(
            extractLinks(self._get_text(doc2)),
            ('http://nohost/plone/doc1',
             'http://nohost/plone/folder1/doc3',
             'http://nohost/plone/image1')
        )

    def test_broken_references(self):
        doc1 = self.portal.doc1
        self.assertEqual(
            len(self.reference_interface(doc1).getReferences()), 0)
        modified(doc1)
        self.assertEqual(
            len(self.reference_interface(doc1).getReferences()), 1)
        self.assertEqual(
            self.reference_interface(doc1).getReferences()[0].id,
            self.portal.doc2.id
        )

        # TODO: Delete item and check again

    def test_relative_upwards_link_generates_matching_reference(self):
        doc3 = self.portal.folder1.doc3
        self._set_text(doc3, '<a href="../folder1">go!</a>')
        self.assertEqual(
            self.reference_interface(doc3).getReferences(),
            [self.portal.folder1]
        )

    # def test_references_to_non_accessible_content_are_generated(self):
    #     secret = self.portal[self.portal.invokeFactory('Document', id='secret')]
    #     from_member = self.portal[self.portal.invokeFactory('Document',
    #                                                         id='member')]
    #     from_member.manage_setLocalRoles('member', ['Contributor'])
    #     secret = self.portal[self.portal.invokeFactory('Document', id='secret')]
    #     # somebody created a document to which the user has no access...
    #     checkPermission = self.portal.portal_membership.checkPermission
    #     logout()
    #     login(self.portal, 'member')
    #     self.assertFalse(checkPermission('View', secret))
    #     self.assertFalse(checkPermission('Access contents information', secret))

    #     # nevertheless it should be possible to set a link to it...
    #     from_member.text = '<html><body><a href="{0:s}">go!</a></body></html>'\
    #         .format(secret.absolute_url())

    #     modified(from_member)
    #     self.assertEqual(IReferenceable(from_member).getReferences(), [secret])


class ReferenceGenerationATTests(ReferenceGenerationDXTests):

    layer = PLONE_APP_LINKINTEGRITY_AT_INTEGRATION_TESTING

    def setText(self, obj, value):
        obj.setText(value)
        notify(ObjectModifiedEvent(obj))

    reference_interface = IATReferenceable

    def _set_text(self, obj, text):
        obj.setText(text)
        modified(obj)

    def _get_text(self, obj):
        return obj.getText()
