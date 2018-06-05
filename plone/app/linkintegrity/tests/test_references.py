# -*- coding: utf-8 -*-
from plone.app.linkintegrity import testing
from plone.app.linkintegrity.parser import extractLinks
from plone.app.linkintegrity.tests.base import DXBaseTestCase
from plone.app.linkintegrity.utils import getIncomingLinks
from plone.app.linkintegrity.utils import getOutgoingLinks
from plone.app.linkintegrity.utils import hasIncomingLinks
from plone.app.linkintegrity.utils import hasOutgoingLinks
from plone.app.testing import login
from plone.app.testing import logout
from plone.app.testing import TEST_USER_NAME
from z3c.relationfield import RelationValue
from z3c.relationfield.event import _setRelation
from zc.relation.interfaces import ICatalog
from zope.component import getUtility
from zope.intid.interfaces import IIntIds
from zope.lifecycleevent import modified

import six


class ReferenceGenerationTestCase:

    def test_is_linked(self):
        img1 = self.portal['image1']
        doc1 = self.portal['doc1']
        self._set_text(doc1, '<img src="image1"></img>')
        self.assertTrue(hasIncomingLinks(img1))

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

        # The warning is shown.
        self.assertTrue(hasOutgoingLinks(doc))
        view = img.restrictedTraverse('delete_confirmation')
        results = view()
        self.assertIn('Potential link breakage', results)
        self.assertIn('The item is not accessible.', results)

        # delete linked item and check if the source still has the relation

        # TODO: There is a permission-problem. Deleting the relation
        # When deleting the linked obj the relation is deleted by
        # z3c.relationfield.event.breakRelations. That also fires
        # ObjectModifiedEvent on the linked obj even though the user might not
        # have the permission to edit that obj.
        # Here plone.app.versioningbehavior.subscribers.create_version_on_save
        # for the linked object is triggerted and results in
        # Unauthorized: You are not allowed to access 'save' in this context

        # self.portal.manage_delObjects(img.id)
        self.portal._delObject(img.id, suppress_events=True)

        logout()
        login(self.portal, TEST_USER_NAME)
        modified(doc)
        self.assertFalse(hasOutgoingLinks(doc))
        # doc now has a broken link and no relation :-(

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

        self.assertEqual(len(list(getOutgoingLinks(doc1))), 0)
        self._set_text(doc1, '<a href="doc1a">Doc 1a</a>')
        self.assertEqual(len(list(getOutgoingLinks(doc1))), 1)
        self.assertEqual([l.to_object for l in getOutgoingLinks(doc1)],
                         [self.portal.doc1a])

        # Now delete the target item, suppress events and test again,
        # the reference should be gone now.
        self.portal._delObject(doc1a.id, suppress_events=True)
        self.assertEqual([l.to_object for l in getOutgoingLinks(doc1)], [None])

    def test_relative_upwards_link_generates_matching_reference(self):
        doc1 = self.portal.doc1
        doc3 = self.portal.folder1.doc3
        self._set_text(doc3, '<a href="../doc1">go!</a>')
        self.assertEqual(len(list(getOutgoingLinks(doc1))), 0)
        self.assertEqual([l.to_object for l in getOutgoingLinks(doc3)],
                         [doc1])

    def test_unicode_links(self):
        doc1 = self.portal.doc1

        # This tests checks that hasIncomingLinks can now be used safely as it
        # eventually plays well with transaction machinery.
        # Add bad link, should not raise exception and there should not
        # be any references added.
        self._set_text(
            doc1,
            '<a href="ö?foo=bar&baz=bam">bug</a>')

        self.assertEqual([l for l in getOutgoingLinks(doc1)], [])

    def test_reference_orthogonality(self):
        doc = self.portal.doc1
        img = self.portal.image1
        tag = img.restrictedTraverse('@@images').tag()

        # This tests the behavior when other references already exist.
        self.assertEqual([l for l in getOutgoingLinks(doc)], [])
        self.assertEqual([l for l in getIncomingLinks(doc)], [])
        self.assertEqual([l for l in getOutgoingLinks(img)], [])
        self.assertEqual([l for l in getOutgoingLinks(img)], [])

        # Then establish a reference between the document and image as
        # a related item:
        self._set_related_items(doc, [img, ])
        self.assertEqual(self._get_related_items(doc), [img, ])

        # Next edit the document body and insert a link to the image,
        # which should trigger the creation of a link integrity reference:
        self._set_text(doc, tag)

        self.assertEqual([l.to_object for l in getOutgoingLinks(doc)], [img])

        # And the related item reference remains in place:
        self.assertEqual(self._get_related_items(doc), [img, ])

        # Finally, edit the document body again, this time removing the
        # link to the image, which should trigger the removal of the
        # link integrity reference:
        self._set_text(doc, 'where did my link go?')
        self.assertEqual([l.to_object for l in getOutgoingLinks(doc)], [])

        # And again the related item reference remains in place:
        self.assertEqual(self._get_related_items(doc), [img, ])

    def test_delete_confirmation_for_any_reference(self):
        """Test, if delete confirmation shows also a warning if items are
        deleted, which are referenced by other items via a reference field.
        """
        img1 = self.portal['image1']
        doc1 = self.portal['doc1']

        intids_tool = getUtility(IIntIds)
        to_id = intids_tool.getId(img1)
        rel = RelationValue(to_id)
        _setRelation(doc1, 'related_image', rel)

        # Test, if relation is present in the relation catalog
        catalog = getUtility(ICatalog)
        rels = list(catalog.findRelations({'to_id':  to_id}))
        self.assertEqual(len(rels), 1)

        # Test, if delete_confirmation_info shows also other relations than
        # ``isReferencing``.
        info = img1.restrictedTraverse('@@delete_confirmation_info')
        breaches = info.get_breaches()
        self.assertEqual(len(breaches), 1)
        self.assertEqual(len(info.get_breaches()[0]['sources']), 1)


class ReferenceGenerationDXTestCase(
    DXBaseTestCase,
    ReferenceGenerationTestCase,
):
    """Reference generation testcase for dx content types"""

if six.PY2:
    from plone.app.linkintegrity.tests.base import ATBaseTestCase

    class ReferenceGenerationATTestCase(
        ATBaseTestCase,
        ReferenceGenerationTestCase,
    ):
        """Reference generation testcase for at content types"""
