# -*- coding: utf-8 -*-
from Products.Archetypes.interfaces import IReferenceable as IATReferenceable
from plone.app.referenceablebehavior.referenceable \
    import IReferenceable as IDXReferenceable
from plone.app.testing import setRoles
from plone.app.testing import logout
from plone.app.testing import login
from plone.app.testing import TEST_USER_ID
from plone.app.testing import TEST_USER_NAME
from plone.app.testing import TEST_USER_PASSWORD
from plone.app.textfield import RichTextValue
from plone.app.linkintegrity import exceptions
from plone.app.linkintegrity.parser import extractLinks
from plone.app.linkintegrity import testing
from plone.testing.z2 import Browser
from zope.lifecycleevent import modified

import transaction
import unittest


class ReferenceGenerationDXTests(unittest.TestCase):

    layer = testing.PLONE_APP_LINKINTEGRITY_DX_INTEGRATION_TESTING
    reference_interface = IDXReferenceable

    def setUp(self):
        self.portal = self.layer['portal']
        self.request = self.layer['request']

        transaction.commit()

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

    def _get_text(self, obj):
        return getattr(obj, 'text')

    def test_notification_exception(self):
        self._set_text(self.portal['doc3'], '<a href="doc1">doc1</a>')
        self.assertRaises(
            exceptions.LinkIntegrityNotificationException,
            self.portal.manage_delObjects, ['doc1'])

    def test_circular_reference_deletion(self):
        login(self.portal, TEST_USER_NAME)
        doc1 = self.portal['doc1']
        doc2 = self.portal['doc2']
        doc3 = self.portal['doc3']
        self._set_text(doc1, '<a href="doc2">doc2</a>')
        self._set_text(doc2, '<a href="doc3">doc3</a>')
        self._set_text(doc3, '<a href="doc1">doc1</a>')
        self.assertRaises(exceptions.LinkIntegrityNotificationException,
                          self.portal.manage_delObjects, ['doc1'])
        transaction.abort()
        self.portal.manage_delObjects(
            ['doc1', 'doc2', 'doc3'], self.request)
        self.assertNotIn('doc1', self.portal)
        self.assertNotIn('doc2', self.portal)
        self.assertNotIn('doc3', self.portal)

    def test_is_linked(self):
        from Products.CMFPlone.utils import isLinked
        img1 = self.portal['image1']
        doc1 = self.portal['doc1']
        self._set_text(doc1, '<img src="image1"></img>')
        self.assertTrue(isLinked(img1))

    def test_references_to_non_accessible_content_are_generated(self):
        secret = self.portal[
            self.portal.invokeFactory('Document', id='secret')]
        from_member = self.portal[
            self.portal.invokeFactory('Document', id='member')]
        from_member.manage_setLocalRoles('member', ['Contributor'])

        # somebody created a document to which the user has no access...
        checkPermission = self.portal.portal_membership.checkPermission
        logout()
        login(self.portal, 'member')
        self.assertFalse(checkPermission('View', secret))
        self.assertFalse(
            checkPermission('Access contents information', secret))

    def test_link_extraction_easy(self):
        doc1 = self.portal.doc1
        self._set_text(doc1, '<a href="doc2">Doc 2</a>')
        self.assertEqual(
            extractLinks(self._get_text(doc1)),
            ('http://nohost/plone/doc2', )
        )

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
        # create a temporary document to test with
        doc1a = testing.create(self.portal, 'Document', id='doc1a')
        doc1 = self.portal.doc1

        # A little hack but allows us to use common syntax
        IReferenceable = self.reference_interface
        self.assertEqual(len(IReferenceable(doc1).getReferences()), 0)
        self._set_text(doc1, '<a href="doc1a">Doc 1a</a>')
        self.assertEqual(len(IReferenceable(doc1).getReferences()), 1)
        self.assertEqual(IReferenceable(doc1).getReferences()[0].id,
                         self.portal.doc1a.id)

        # Now delete the target item, suppress events and test again:
        self.portal.manage_delObjects(ids=[doc1a.id], suppress_events=1)
        self.assertEqual(len(IReferenceable(doc1).getReferences()), 1)

        import pdb; pdb.set_trace( )
        # TODO: Delete item and check again

    def test_relative_upwards_link_generates_matching_reference(self):
        doc3 = self.portal.folder1.doc3
        self._set_text(doc3, '<a href="../folder1">go!</a>')

        # A little hack but allows us to use common syntax
        IReferenceable = self.reference_interface

        self.assertEqual(
            IReferenceable(doc3).getReferences(),
            [self.portal.folder1]
        )

        secret = testing.create(self.portal, 'Document', id='secret')
        from_member = testing.create(self.portal, 'Document', id='member')
        from_member.manage_setLocalRoles('member', ['Contributor'])

        # somebody created a document to which the user has no access...
        checkPermission = self.portal.portal_membership.checkPermission
        logout()
        login(self.portal, 'member')
        self.assertFalse(checkPermission('View', secret))
        self.assertFalse(checkPermission('Access contents information', secret))

        # nevertheless it should be possible to set a link to it...
        from_member.text = \
            '<a href="{0:s}">go!</a>'.format(secret.absolute_url())

        modified(from_member)
        self.assertEqual(IReferenceable(from_member).getReferences(), [secret])


class ReferenceGenerationATTests(ReferenceGenerationDXTests):

    layer = testing.PLONE_APP_LINKINTEGRITY_AT_INTEGRATION_TESTING
    reference_interface = IATReferenceable

    def _set_text(self, obj, text):
        obj.setText(text)
        modified(obj)

    def _get_text(self, obj):
        return obj.getText()
