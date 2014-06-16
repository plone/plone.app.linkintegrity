# -*- coding: utf-8 -*-
from Products.Archetypes.interfaces import IReferenceable
from plone.app.linkintegrity import testing
from plone.app.testing import logout
from plone.app.testing import login
from plone.app.linkintegrity import exceptions
from plone.app.linkintegrity.parser import extractLinks
from plone.app.linkintegrity.tests.base import ATBaseTestCase
from plone.app.linkintegrity.tests.base import DXBaseTestCase


class ReferenceGenerationTestCase:

    def test_notification_exception(self):
        self._set_text(self.portal['doc3'], '<a href="doc1">doc1</a>')
        self.assertRaises(
            exceptions.LinkIntegrityNotificationException,
            self.portal.manage_delObjects, ['doc1'])

    def test_is_linked(self):
        from Products.CMFPlone.utils import isLinked
        img1 = self.portal['image1']
        doc1 = self.portal['doc1']
        self._set_text(doc1, '<img src="image1"></img>')
        self.assertTrue(isLinked(img1))

    def test_referal_to_private_files(self):
        # This tests the behaviour of the link integrity code when a to
        # be deleted item is referred to by some page the current user
        # has no permission to view. In this case the privacy of the
        # linking user should be protected, so neither the name or url
        # of the linking page should be shown. First we need to create
        # the link in question and set up the permissions accordingly.
        doc = self.portal.doc1
        img = self.portal.image1
        self._set_text(doc, '<a href="image1">Image 1</a>')

        roles = ('Member', )
        self.portal.manage_permission('List folder contents', roles=roles)
        self.portal.manage_permission('Delete objects', roles=roles)
        doc.manage_permission('View', roles=('Manager',), acquire=0)
        doc.manage_permission('Access contents information',
                              roles=('Manager', ), acquire=0)

        logout()
        login(self.portal, 'member')
        checkPermission = self.portal.portal_membership.checkPermission
        self.assertFalse(checkPermission('View', doc))
        self.assertFalse(checkPermission('Access contents information', doc))
        self.assertTrue(checkPermission('View', img))
        self.assertTrue(checkPermission('Access contents information', img))

        token = self._get_token(img)
        self.request['_authenticator'] = token

        # Throws exception
        view = img.restrictedTraverse('@@object_delete')
        self.assertRaises(exceptions.LinkIntegrityNotificationException, view)

    def test_link_extraction_easy(self):
        doc1 = self.portal.doc1
        self._set_text(doc1, '<a href="doc2">Doc 2</a>')
        self.assertEqual(
            extractLinks(self._get_text(doc1)),
            ('doc2', )
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
            ('doc1',
             'folder1/doc3',
             'image1')
        )

    def test_broken_references(self):
        # create a temporary document to test with
        doc1a = testing.create(self.portal, 'Document', id='doc1a')
        doc1 = self.portal.doc1

        self.assertEqual(len(IReferenceable(doc1).getReferences()), 0)
        self._set_text(doc1, '<a href="doc1a">Doc 1a</a>')
        self.assertEqual(len(IReferenceable(doc1).getReferences()), 1)
        self.assertEqual(IReferenceable(doc1).getReferences()[0].id,
                         self.portal.doc1a.id)

        # Now delete the target item, suppress events and test again,
        # the reference should be broken now.
        self.portal._delObject(doc1a.id, suppress_events=True)
        self.assertEqual(IReferenceable(doc1).getReferences(), [None])

        # If we now try to update the linking document again in order to
        # remove the link, things used to break raising a
        # ``ReferenceException``.  This should be handled more
        # gracefully now:
        self._set_text(doc1, 'foo!')
        self.assertEqual(IReferenceable(doc1).getReferences(), [])

    def test_relative_upwards_link_generates_matching_reference(self):
        doc1 = self.portal.doc1
        doc3 = self.portal.folder1.doc3
        self._set_text(doc3, '<a href="../doc1">go!</a>')
        self.assertEqual(IReferenceable(doc3).getReferences(), [doc1])

    def test_unicode_links(self):
        doc1 = self.portal.doc1

        # This tests checks that isLinked can now be used safely as it
        # eventually plays well with transaction machinery.
        # Add bad link, should not raise exception and there should not
        # be any references added.
        self._set_text(doc1, unicode('<a href="ö?foo=bar&baz=bam">bug</a>', 'utf-8'))
        self.assertEqual(IReferenceable(doc1).getReferences(), [])

    def test_reference_orthogonality(self):
        doc = self.portal.doc1
        img = self.portal.image1
        tag = img.restrictedTraverse('@@images').tag()

        # This tests the behavior when other references already exist.
        self.assertEqual(IReferenceable(doc).getReferences(), [])
        self.assertEqual(IReferenceable(doc).getBackReferences(), [])
        self.assertEqual(IReferenceable(img).getReferences(), [])
        self.assertEqual(IReferenceable(img).getBackReferences(), [])

        # Then establish a reference between the document and image as
        # a related item:
        self._set_related_items(doc, [img, ])
        self.assertEqual(self._get_related_items(doc), [img, ])

        # Next edit the document body and insert a link to the image,
        # which should trigger the creation of a link integrity reference:
        self._set_text(doc, tag)

        from plone.app.linkintegrity.handlers import referencedRelationship
        self.assertEqual(IReferenceable(doc).getReferences(
            relationship=referencedRelationship), [img, ])

        # And the related item reference remains in place:
        self.assertEqual(self._get_related_items(doc), [img, ])

        # Finally, edit the document body again, this time removing the
        # link to the image, which should trigger the removal of the
        # link integrity reference:
        self._set_text(doc, 'where did my link go?')
        self.assertEqual(IReferenceable(doc).getReferences(
            relationship=referencedRelationship), [])

        # And again the related item reference remains in place:
        self.assertEqual(self._get_related_items(doc), [img, ])


class ReferenceGenerationDXTestCase(DXBaseTestCase, ReferenceGenerationTestCase):
    """Reference generation testcase for dx content types"""


class ReferenceGenerationATTestCase(ATBaseTestCase, ReferenceGenerationTestCase):
    """Reference generation testcase for at content types"""
