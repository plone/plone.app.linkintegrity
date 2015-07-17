# -*- coding: utf-8 -*-
from Products.Archetypes.interfaces import IReferenceable
from plone.app.linkintegrity.parser import extractLinks
from plone.app.linkintegrity.handlers import referencedRelationship

from plone.app.linkintegrity.tests.base import ATBaseTestCase
from plone.app.linkintegrity.tests.base import DXBaseTestCase
from plone.app.linkintegrity.upgrades import migrate_linkintegrity_relations
from plone.app.testing import login
from plone.app.testing import logout
from plone.app.linkintegrity.utils import hasIncomingLinks


class TestUpgrades(object):

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


# class ReferenceGenerationDXTestCase(DXBaseTestCase, TestUpgrades):
#     """Reference generation testcase for dx content types"""


class ReferenceGenerationATTestCase(ATBaseTestCase, TestUpgrades):
    """Reference generation testcase for at content types"""
