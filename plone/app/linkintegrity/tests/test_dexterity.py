# -*- coding: utf-8 -*-
"""Tests for dexterity content."""
import unittest
import pkg_resources
import zope.event
from zExceptions import BadRequest
from Acquisition import aq_base
from zope.interface import Interface, alsoProvides
from zope.lifecycleevent import ObjectModifiedEvent
from plone.uuid.interfaces import IMutableUUID
from plone.uuid.interfaces import IUUIDGenerator
from zope.component import getUtility
from OFS.CopySupport import CopyError
from plone.app.linkintegrity.tests import layer, utils
from Products.PloneTestCase import PloneTestCase


try:
    pkg_resources.get_distribution('plone.app.referenceablebehavior')
except pkg_resources.DistributionNotFound:
    HAS_DEXTERITY = False
    pass
else:
    HAS_DEXTERITY = True
    from plone.dexterity.fti import DexterityFTI
    from plone.app.textfield import RichText
    from plone.app.textfield.value import RichTextValue
    class IMyDexterityItem(Interface):
        text = RichText(title=u'Text')

PloneTestCase.setupPloneSite()


class TestDexterityContent(PloneTestCase.PloneTestCase):
    """Unit tests for dexterity content"""

    layer = layer.integrity

    def afterSetUp(self):
        """ create some sample content to test with """
        if not HAS_DEXTERITY:
            return
        self.setRoles(('Manager',))
        fti = DexterityFTI('My Dexterity Item')
        self.portal.portal_types._setObject('My Dexterity Item', fti)
        fti.klass = 'plone.dexterity.content.Item'
        fti.schema = 'plone.app.linkintegrity.tests.test_dexterity.IMyDexterityItem'
        fti.behaviors = ('plone.app.referenceablebehavior.referenceable.IReferenceable',)
        fti = DexterityFTI('Non referenciable Dexterity Item')
        self.portal.portal_types._setObject('Non referenciable Dexterity Item', fti)
        fti.klass = 'plone.dexterity.content.Item'
        fti.schema = 'plone.app.linkintegrity.tests.test_dexterity.IMyDexterityItem'
        
    def test_referenciable_dexterity(self):
        """ Test Dexterity linkintegrity """
        if not HAS_DEXTERITY:
            return

        portal = self.portal
        self.setRoles(('Manager',))
        portal.invokeFactory('My Dexterity Item', id='dexterity_item1')
        portal.invokeFactory('My Dexterity Item', id='dexterity_item2')

        portal.dexterity_item1.text = RichTextValue(raw='<html> <body> <a href="doc1" /> </body> </html>',
                                                    mimeType='text/html')
        zope.event.notify(ObjectModifiedEvent(portal.dexterity_item1))
        self.assertEqual(portal.reference_catalog(sourceUID=portal.dexterity_item1.UID())[0].targetUID, portal.doc1.UID())

        portal.doc1.setText('<html> <body> <a href="/plone/dexterity_item2" /> </body> </html>')
        zope.event.notify(ObjectModifiedEvent(portal.doc1))
        self.assertEqual(portal.reference_catalog(sourceUID=portal.doc1.UID())[0].targetUID, portal.dexterity_item2.UID())

    def test_nonreferenciable_dexterity(self):
        """ Test Non referenciable Dexterity content """
        if not HAS_DEXTERITY:
            return

        portal = self.portal
        self.setRoles(('Manager',))
        portal.invokeFactory('Non referenciable Dexterity Item',
                             id='nonreferenciable_dexterity_item1')

        portal.nonreferenciable_dexterity_item1.text = RichTextValue(raw='<html> <body> <a href="doc1" /> </body> </html>',
                                                                     mimeType='text/html')
        zope.event.notify(ObjectModifiedEvent(portal.nonreferenciable_dexterity_item1))
        self.assertFalse(portal.reference_catalog(sourceUID=portal.nonreferenciable_dexterity_item1.UID()))
