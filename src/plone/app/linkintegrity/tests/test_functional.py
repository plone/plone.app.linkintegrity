"""Functional tests for link integrity that stay in plone.app.linkintegrity.

Only tests that verify behaviour independent of HTML rendering belong here.
All HTML-rendering tests (delete confirmation page with "Potential link
breakage") live in plone.app.layout.tests.test_linkintegrity.
"""

from plone.app.linkintegrity import testing
from plone.app.linkintegrity.tests.utils import set_text
from plone.app.linkintegrity.utils import getOutgoingLinks
from plone.app.testing import TEST_USER_NAME
from plone.app.testing import TEST_USER_PASSWORD
from plone.testing.zope import Browser

import transaction
import unittest


class FunctionalReferenceTestCase(unittest.TestCase):
    """Functional tests for link integrity behaviour (no HTML assertions)."""

    layer = testing.PLONE_APP_LINKINTEGRITY_FUNCTIONAL_TESTING

    def setUp(self):
        self.portal = self.layer["portal"]
        self.request = self.layer["request"]

        self.browser = Browser(self.layer["app"])
        self.browser.handleErrors = False
        self.browser.addHeader("Referer", self.portal.absolute_url())
        self.browser.addHeader(
            "Authorization", f"Basic {TEST_USER_NAME}:{TEST_USER_PASSWORD}"
        )
        self.browser.open(self.portal.absolute_url())

    def test_unreferenced_removal(self):
        # Simple removal of a not-referenced item must work without errors
        # (regression for #6666 and #7784 which broke ZEO-based installs).
        self.browser.open(self.portal.doc1.absolute_url())
        self.browser.getLink("Delete").click()
        self.assertIn("Do you really want to delete this item?", self.browser.contents)
        self.browser.getControl(name="form.buttons.Delete").click()
        self.assertIn("Test Page 1 has been deleted", self.browser.contents)
        self.assertNotIn("doc1", self.portal.objectIds())

    def test_removal_via_zmi(self):
        """Delete via ZMI is not protected by link integrity."""
        doc1 = self.portal.doc1
        doc2 = self.portal.doc2

        set_text(doc1, '<a href="doc2">a document</a>')
        self.assertEqual([i.to_object for i in getOutgoingLinks(doc1)], [doc2])
        transaction.commit()

        self.browser.handleErrors = True
        self.browser.open("http://nohost/plone/manage_main")
        self.browser.getControl(name="ids:list").getControl(value="doc2").selected = (
            True
        )
        self.browser.getControl("Delete").click()
        self.assertNotIn("doc2", self.portal.objectIds())
