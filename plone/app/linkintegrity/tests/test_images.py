# -*- coding: utf-8 -*-
from Products.Archetypes.interfaces import IReferenceable
from plone.app.linkintegrity.tests.base import ATBaseTestCase
from plone.app.linkintegrity.tests.base import DXBaseTestCase
from plone.uuid.interfaces import IUUID


class ImageReferenceTestCase:

    def test_image_tag_reference_creation(self):
        doc1 = self.portal.doc1
        img1 = self.portal.image1

        # This tests the correct creation of references used for
        # ensuring link integrity. Any archetype-based content object
        # which refers to other (local) objects by `<img>` or `<a>` tags
        # should create references between those objects on save.
        self._set_text(doc1, img1.restrictedTraverse('@@images').tag())

        self.assertEqual(IReferenceable(doc1).getReferences(), [img1])
        self.assertEqual(IReferenceable(doc1).getBackReferences(), [])
        self.assertEqual(IReferenceable(img1).getReferences(), [])
        self.assertEqual(IReferenceable(img1).getBackReferences(), [doc1])

    def test_image_scale_reference_creation(self):
        doc1 = self.portal.doc1
        img1 = self.portal.image1

        # Linking image scales should also work:
        self._set_text(
            doc1, '<a href="image1/@@images/image_thumb">an image</a>')
        self.assertEqual(IReferenceable(doc1).getReferences(), [img1])
        self.assertEqual(IReferenceable(img1).getBackReferences(), [doc1])

    def test_image_resolveuid_reference_creation(self):
        doc1 = self.portal.doc1
        img1 = self.portal.image1

        # Linking via the "resolveuid/UID" method should also work:
        self._set_text(doc1, '<a href="resolveuid/{0:s}">an image</a>'.format(
            IUUID(img1)))

        self.assertEqual(IReferenceable(doc1).getReferences(), [img1])
        self.assertEqual(IReferenceable(img1).getBackReferences(), [doc1])


class ImageReferenceDXTestCase(DXBaseTestCase, ImageReferenceTestCase):
    """Image reference testcase for dx content types"""


class ImageReferenceATTestCase(ATBaseTestCase, ImageReferenceTestCase):
    """Image reference testcase for dx content types"""
