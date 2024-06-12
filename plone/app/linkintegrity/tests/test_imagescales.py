from plone.app.linkintegrity import testing
from plone.app.linkintegrity.tests.utils import set_text
from plone.app.linkintegrity.utils import getIncomingLinks
from plone.app.linkintegrity.utils import getOutgoingLinks
from plone.uuid.interfaces import IUUID

import unittest


class ImageReferenceTestCase(unittest.TestCase):
    """image reference testcase"""

    layer = testing.PLONE_APP_LINKINTEGRITY_INTEGRATION_TESTING

    def setUp(self):
        self.portal = self.layer["portal"]

    def test_image_tag_reference_creation(self):
        doc1 = self.portal.doc1
        img1 = self.portal.image1

        # This tests the correct creation of references used for
        # ensuring link integrity. Any archetype-based content object
        # which refers to other (local) objects by `<img>` or `<a>` tags
        # should create references between those objects on save.
        set_text(doc1, img1.restrictedTraverse("@@images").tag())

        self.assertEqual(
            [r.to_object for r in getOutgoingLinks(doc1)],
            [
                img1,
            ],
        )
        self.assertEqual([r.to_object for r in getIncomingLinks(doc1)], [])
        self.assertEqual([r.to_object for r in getOutgoingLinks(img1)], [])
        self.assertEqual(
            [r.from_object for r in getIncomingLinks(img1)],
            [doc1],
        )

    def test_image_scale_reference_creation(self):
        doc1 = self.portal.doc1
        img1 = self.portal.image1

        # Linking image scales should also work:
        set_text(doc1, '<a href="image1/@@images/image_thumb">an image</a>')
        self.assertEqual(
            [r.to_object for r in getOutgoingLinks(doc1)],
            [
                img1,
            ],
        )
        self.assertEqual(
            [r.from_object for r in getIncomingLinks(img1)],
            [
                doc1,
            ],
        )

    def test_image_resolveuid_reference_creation(self):
        doc1 = self.portal.doc1
        img1 = self.portal.image1

        # Linking via the "resolveuid/UID" method should also work:
        set_text(doc1, f'<a href="resolveuid/{IUUID(img1):s}">an image</a>')
        self.assertEqual(
            [r.to_object for r in getOutgoingLinks(doc1)],
            [
                img1,
            ],
        )
        self.assertEqual(
            [r.from_object for r in getIncomingLinks(img1)],
            [
                doc1,
            ],
        )
