# -*- coding: utf-8 -*-
from Products.Archetypes.interfaces import IReferenceable
from plone.app.linkintegrity import exceptions
from plone.app.linkintegrity import testing
from plone.app.linkintegrity.tests.base import ATBaseTestCase
from plone.app.linkintegrity.tests.base import DXBaseTestCase

import transaction


class CircularReferencesTestCase:

    def test_circular_reference_deletion(self):
        doc1 = self.portal['doc1']
        doc2 = self.portal['doc2']
        doc3 = self.portal['doc3']
        self._set_text(doc1, '<a href="doc2">doc2</a>')
        self._set_text(doc2, '<a href="doc3">doc3</a>')
        self._set_text(doc3, '<a href="doc1">doc1</a>')
        self.assertRaises(
            exceptions.LinkIntegrityNotificationException,
            self.portal.manage_delObjects, ['doc1'], self.request
        )
        transaction.abort()

        self.portal.manage_delObjects(
            ['doc1', 'doc2', 'doc3'], self.request)
        self.assertNotIn('doc1', self.portal)
        self.assertNotIn('doc2', self.portal)
        self.assertNotIn('doc3', self.portal)

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
        self.assertEqual(IReferenceable(doc1).getReferences(), [doc2, ])
        self.assertEqual(IReferenceable(doc2).getReferences(), [doc4, ])
        self.assertEqual(IReferenceable(doc4).getReferences(), [doc1, ])

        self.assertRaises(exceptions.LinkIntegrityNotificationException,
            self.portal.manage_delObjects, ['doc1', 'doc2', ], self.request)
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
