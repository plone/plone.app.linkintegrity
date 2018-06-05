# -*- coding: utf-8 -*-
from plone.app.linkintegrity.upgrades import migrate_linkintegrity_relations
from plone.app.linkintegrity.utils import hasIncomingLinks
from plone.app.linkintegrity.utils import referencedRelationship
try:
    from Products.Archetypes.interfaces import IReferenceable
    from plone.app.linkintegrity.tests.base import ATBaseTestCase
    HAS_AT = True
except ImportError:
    HAS_AT = False
import unittest


if HAS_AT:
    class ReferenceMigrationATTestCase(ATBaseTestCase):
        """Reference migration testcase for at content types"""

        @unittest.skipUnless(
            HAS_AT, 'Archetypes are not installed. Skipping migration tests')
        def test_upgrade(self):
            doc3 = self.portal['doc3']
            doc1 = self.portal['doc1']
            self.assertTrue(IReferenceable.providedBy(doc3))
            doc3.setText('<a href="doc1">doc1</a>', mimetype='text/html')
            doc3.addReference(doc1, relationship=referencedRelationship)
            self.assertFalse(hasIncomingLinks(doc1))
            self.assertFalse(hasIncomingLinks(doc3))
            migrate_linkintegrity_relations(self.portal)
            self.assertTrue(hasIncomingLinks(doc1))
            self.assertFalse(hasIncomingLinks(doc3))

else:

    class TestDummy(unittest.TestCase):

        def test_dummy(self):
            pass
