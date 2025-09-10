from plone.app.linkintegrity import testing
from plone.app.linkintegrity.browser.info import DeleteConfirmationInfo
from plone.app.linkintegrity.tests.utils import set_text

import unittest


class DeleteConfirmationInfoTestCase(unittest.TestCase):
    layer = testing.PLONE_APP_LINKINTEGRITY_INTEGRATION_TESTING

    def setUp(self):
        self.portal = self.layer["portal"]
        self.request = self.layer["request"]

    def test_get_breaches_shape(self):
        # Just here as a sanity check.
        folder1 = self.portal.folder1
        doc1 = self.portal.doc1
        set_text(doc1, '<a href="folder1">f1</a>')
        view = DeleteConfirmationInfo(self.portal, self.request)
        self.assertEqual(
            view.get_breaches([folder1]),
            [
                {
                    "target": {
                        "uid": folder1.UID(),
                        "title": "Folder 1",
                        "url": "http://nohost/plone/folder1",
                        "portal_type": "Folder",
                        "type_title": "Folder",
                    },
                    "sources": [
                        {
                            "uid": doc1.UID(),
                            "title": "Test Page 1",
                            "url": "http://nohost/plone/doc1",
                            "accessible": 1,
                        }
                    ],
                }
            ],
        )
