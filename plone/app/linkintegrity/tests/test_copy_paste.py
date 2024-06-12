from plone.app.linkintegrity.testing import PLONE_APP_LINKINTEGRITY_INTEGRATION_TESTING
from plone.app.testing import setRoles
from plone.app.testing import TEST_USER_ID
from plone.app.textfield import RichTextValue
from zope.lifecycleevent import modified

import unittest


class TestCopyPaste(unittest.TestCase):

    layer = PLONE_APP_LINKINTEGRITY_INTEGRATION_TESTING

    def setUp(self):
        self.portal = self.layer["portal"]
        self.request = self.layer["request"]
        setRoles(self.portal, TEST_USER_ID, ["Manager"])

    def test_copy_paste(self):
        """Test that https://github.com/plone/Products.CMFPlone/issues/2866
        is fixed. Setting relations during copy&paste failed in Zope 4.
        """
        self.portal.invokeFactory("Image", "image", title="Image")
        self.portal.invokeFactory("Document", "document", title="Document")
        document = self.portal["document"]
        image = self.portal["image"]
        text = RichTextValue(
            '<p><img src="{portal}/resolveuid/{uid}/@@images/image/large" class="image-inline" data-linktype="image" data-scale="large" data-val="{uid}" data-mce-src="{portal}/resolveuid/{uid}/@@images/image/large" data-mce-selected="1"></p>'.format(
                portal="..", uid=image.UID()
            ),
            "text/html",
            "text/x-html-safe",
        )
        document.text = text
        modified(document)
        self.portal.invokeFactory("Folder", "folder", title="Folder")
        target = self.portal["folder"]

        copied = self.portal.manage_copyObjects("document")
        target.manage_pasteObjects(copied)
        self.assertTrue(target["document"])
        # check that linkintegrity-relations exists for both items:
        info = image.restrictedTraverse("@@delete_confirmation_info")
        breaches = info.get_breaches()
        self.assertEqual(len(breaches[0]["sources"]), 2)
        uids_objs = [i.UID() for i in [target["document"], document]]
        uids_rels = [i["uid"] for i in breaches[0]["sources"]]
        self.assertEqual(set(uids_objs), set(uids_rels))
