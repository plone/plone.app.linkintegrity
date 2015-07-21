# -*- coding: utf-8 -*-
from plone.app.linkintegrity.tests.base import ATBaseTestCase
from plone.app.linkintegrity.tests.base import DXBaseTestCase
from plone.app.linkintegrity.utils import hasIncomingLinks
from plone.app.linkintegrity.utils import getOutgoingLinks
from plone.app.linkintegrity.browser.info import DeleteConfirmationInfo

import transaction


class CircularReferencesTestCase:

    def test_circular_reference_manages_relations(self):
        doc1 = self.portal['doc1']
        doc2 = self.portal['doc2']
        doc3 = self.portal['doc3']
        self.assertFalse(hasIncomingLinks(doc1))
        self.assertFalse(hasIncomingLinks(doc2))
        self.assertFalse(hasIncomingLinks(doc3))
        self._set_text(doc1, '<a href="doc2">doc2</a>')
        self._set_text(doc2, '<a href="doc3">doc3</a>')
        self._set_text(doc3, '<a href="doc1">doc1</a>')
        self.assertTrue(hasIncomingLinks(doc1))
        self.assertTrue(hasIncomingLinks(doc2))
        self.assertTrue(hasIncomingLinks(doc3))
        transaction.abort()

        self.portal.manage_delObjects(
            ['doc1', 'doc2', 'doc3'], self.request)
        self.assertNotIn('doc1', self.portal)
        self.assertNotIn('doc2', self.portal)
        self.assertNotIn('doc3', self.portal)
        self.assertRaises(KeyError, hasIncomingLinks, [doc1])
        self.assertRaises(KeyError, hasIncomingLinks, [doc2])
        self.assertRaises(KeyError, hasIncomingLinks, [doc2])

    def test_circular_reference_subfolder_deletion(self):
        doc1 = self.portal.doc1
        doc2 = self.portal.doc2
        doc4 = self.portal.folder1.doc4

        # This tests the behaviour when removing three object
        # referencing each other in a circle.  This situation cannot be
        # resolved completely, since the removal events are fired
        # separately.  However, the circle gets "broken up" when
        # confirming the removal of the first object, and no further
        # confirmation form are necessary:
        self._set_text(doc1, '<a href="doc2">documents...</a>')
        self._set_text(doc2, '<a href="folder1/doc4">linking...</a>')
        self._set_text(doc4, '<a href="../doc1">in circles.</a>')

        self.assertEqual([r.to_object for r in getOutgoingLinks(doc1)], [doc2, ])
        self.assertEqual([r.to_object for r in getOutgoingLinks(doc2)], [doc4, ])
        self.assertEqual([r.to_object for r in getOutgoingLinks(doc4)], [doc1, ])

        view = DeleteConfirmationInfo(self.portal, self.request)
        view.checkObject(doc1)
        view.checkObject(doc2)
        self.assertEqual(len(view.breaches), 2)
        transaction.abort()

        self.portal.manage_delObjects(
            ['doc1', 'doc2', 'folder1', ], self.request)

        self.assertNotIn('doc1', self.portal)
        self.assertNotIn('doc2', self.portal)
        self.assertNotIn('folder1', self.portal)


class CircularReferencesDXTestCase(DXBaseTestCase, CircularReferencesTestCase):
    """Circular reference testcase for dx content types"""


class CircularReferencesATTestCase(ATBaseTestCase, CircularReferencesTestCase):
    """Circular reference testcase for dx content types"""
