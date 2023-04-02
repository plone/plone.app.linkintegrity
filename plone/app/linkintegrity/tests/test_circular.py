from plone.app.linkintegrity import testing
from plone.app.linkintegrity.browser.info import DeleteConfirmationInfo
from plone.app.linkintegrity.testing import create
from plone.app.linkintegrity.tests.utils import set_text
from plone.app.linkintegrity.utils import getOutgoingLinks
from plone.app.linkintegrity.utils import hasIncomingLinks
from plone.app.textfield import RichTextValue
from zope.lifecycleevent import modified

import unittest


class CircularReferencesTestCase(unittest.TestCase):
    """Circular reference testcase"""

    layer = testing.PLONE_APP_LINKINTEGRITY_INTEGRATION_TESTING

    def setUp(self):
        self.portal = self.layer["portal"]
        self.request = self.layer["request"]

    def _set_text(self, obj, text):
        obj.text = RichTextValue(text)
        modified(obj)

    def test_circular_reference_manages_relations(self):
        doc1 = self.portal["doc1"]
        doc2 = self.portal["doc2"]
        doc3 = self.portal["doc3"]
        self.assertFalse(hasIncomingLinks(doc1))
        self.assertFalse(hasIncomingLinks(doc2))
        self.assertFalse(hasIncomingLinks(doc3))
        set_text(doc1, '<a href="doc2">doc2</a>')
        set_text(doc2, '<a href="doc3">doc3</a>')
        set_text(doc3, '<a href="doc1">doc1</a>')
        self.assertTrue(hasIncomingLinks(doc1))
        self.assertTrue(hasIncomingLinks(doc2))
        self.assertTrue(hasIncomingLinks(doc3))

    def test_circular_reference_subfolder_deletion(self):
        doc1 = self.portal.doc1
        doc2 = self.portal.doc2
        doc3 = self.portal.doc3
        doc4 = self.portal.folder1.doc4
        folder1 = self.portal.folder1

        # This tests the behaviour when removing objects
        # referencing each other in a circle.
        set_text(doc1, '<a href="doc2">documents...</a>')
        set_text(doc2, '<a href="doc3">go round...</a>')
        set_text(doc3, '<a href="folder1/doc4">and round.</a>')
        set_text(doc4, '<a href="../doc1">in circles.</a>')

        self.assertEqual([r.to_object for r in getOutgoingLinks(doc1)], [doc2])
        self.assertEqual([r.to_object for r in getOutgoingLinks(doc2)], [doc3])
        self.assertEqual([r.to_object for r in getOutgoingLinks(doc3)], [doc4])
        self.assertEqual([r.to_object for r in getOutgoingLinks(doc4)], [doc1])

        view = DeleteConfirmationInfo(self.portal, self.request)
        self.assertEqual(len(view.get_breaches([folder1])), 1)
        self.assertEqual(len(view.get_breaches([doc1, doc2, doc3, folder1])), 0)
        self.assertEqual(len(view.get_breaches([doc2, folder1])), 2)

    def test_internal_breaches_are_dropped(self):
        folder1 = self.portal.folder1
        create(folder1, "Document", id="doc5", title="Test Page 5")
        doc1 = self.portal.doc1
        doc4 = self.portal.folder1.doc4
        doc5 = self.portal.folder1.doc5
        set_text(doc1, '<a href="folder1">f1</a>')
        set_text(doc4, '<a href="doc5">d5</a><a href="../doc1">d1</a>')
        set_text(doc5, '<a href="../folder1">f1</a>')

        doc4_breaches = {r.to_object for r in getOutgoingLinks(doc4)}
        # the order of breaches is non-deterministic
        self.assertEqual({doc1, doc5}, doc4_breaches)
        self.assertEqual([r.to_object for r in getOutgoingLinks(doc5)], [folder1])
        self.assertEqual([r.to_object for r in getOutgoingLinks(doc1)], [folder1])
        view = DeleteConfirmationInfo(self.portal, self.request)
        self.assertEqual(len(view.get_breaches([doc4])), 0)
        self.assertEqual(len(view.get_breaches([doc5])), 1)
        self.assertEqual(len(view.get_breaches([doc4, doc5])), 0)
        self.assertEqual(len(view.get_breaches([folder1])), 1)
        self.assertEqual(len(view.get_breaches([doc1])), 1)
        self.assertEqual(len(view.get_breaches([doc1, folder1])), 0)

        view = folder1.restrictedTraverse("delete_confirmation")
        self.assertIn("Potential link breakage", view())
        view = folder1.restrictedTraverse("delete_confirmation_info")
        self.assertIn("Potential link breakage", view())
        view = doc4.restrictedTraverse("delete_confirmation")
        self.assertNotIn("Potential link breakage", view())
        view = doc4.restrictedTraverse("delete_confirmation_info")
        self.assertNotIn("Potential link breakage", view())
