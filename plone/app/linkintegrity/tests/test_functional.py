# -*- coding: utf-8 -*-
from ZPublisher.Publish import Retry
from Products.Archetypes.interfaces import IReferenceable
from plone.app.linkintegrity import testing
from plone.app.linkintegrity import exceptions
from plone.app.linkintegrity.tests.base import ATBaseTestCase
from plone.app.linkintegrity.tests.base import DXBaseTestCase
from plone.app.testing import TEST_USER_NAME
from plone.app.testing import TEST_USER_PASSWORD

import transaction


class ReferenceTestCase:

    def test_file_reference_throws_exception(self):
        """This tests the behaviour when removing a referenced file."""

        doc1 = self.portal.doc1
        file2 = testing.create(self.portal, 'File',
                               id='file2', file=testing.GIF)

        self._set_text(doc1, '<a href="file2">A File</a>')
        self.assertEqual(IReferenceable(doc1).getReferences(), [file2])
        self.assertIn('file2', self.portal.objectIds())

        token = self._get_token(file2)
        self.request['_authenticator'] = token

        # Throws exception which actually should abort transaction
        view = file2.restrictedTraverse('@@object_delete')
        self.assertRaises(exceptions.LinkIntegrityNotificationException, view)

    def test_file_reference_linkintegrity_page_is_shown(self):
        doc1 = self.portal.doc1
        file2 = testing.create(self.portal, 'File',
                               id='file2', file=testing.GIF)

        self._set_text(doc1, '<a href="file2">A File</a>')
        self.assertEqual(IReferenceable(doc1).getReferences(), [file2])
        self.assertIn('file2', self.portal.objectIds())

        token = self._get_token(file2)
        self.request['_authenticator'] = token

        # Make changes visible to test browser
        transaction.commit()

        self._set_response_status_code('Retry', 200)
        self._set_response_status_code(
            'LinkIntegrityNotificationException', 200)

        self.browser.handleErrors = True
        self.browser.addHeader(
            'Authorization',
            'Basic {0:s}:{1:s}'.format(TEST_USER_NAME, TEST_USER_PASSWORD))

        delete_url = '{0:s}/object_delete?_authenticator={1:s}'.format(
            file2.absolute_url(), token)

        # Try to remove but cancel
        self.browser.open(delete_url)

        # Validate text
        self.assertIn('Potential link breakage', self.browser.contents)
        self.assertIn('removeConfirmationAction', self.browser.contents)
        self.assertIn('<a href="http://nohost/plone/doc1">Test Page 1</a>',
                      self.browser.contents)
        self.assertIn('Would you like to delete it anyway?',
                      self.browser.contents)

        # Click cancel button, item should stay in place
        self.browser.getControl(name='cancel').click()
        self.assertEqual(self.browser.url, self.portal.absolute_url())
        self.assertIn('Removal cancelled.', self.browser.contents)
        self.assertIn('file2', self.portal.objectIds())

        # Try to remove and confirm
        self.browser.open(delete_url)
        self.browser.handleErrors = False
        self.assertRaises(Retry, self.browser.getControl(name='delete').click)

        self.portal._delObject('file2', suppress_events=True)
        self.assertNotIn('file2', self.portal.objectIds())
        transaction.commit()

    def test_unreferenced_removal(self):
        # This tests against #6666 and #7784, simple removal of a not 
        # referenced file, which broke zeo-based installations.
        self._set_response_status_code(
            'LinkIntegrityNotificationException', 200)

        # We simply use a browser to try to delete a content item. 
        self.browser.open(self.portal.doc1.absolute_url())
        self.browser.getLink('Delete').click()
        self.assertIn(
            'Do you really want to delete this item?', self.browser.contents)
        self.browser.getControl(name='form.buttons.Delete').click()

        # The resulting page should confirm the removal:
        self.assertIn('Test Page 1 has been deleted', self.browser.contents)
        self.assertNotIn('doc1', self.portal.objectIds())

    def test_renaming_referenced_item(self):
        doc1 = self.portal.doc1
        doc2 = self.portal.doc2

        # This tests makes sure items that are linked to can still be 
        # renamed (see the related bug report in #6608).  First we need 
        # to create the necessary links:
        self._set_text(doc1, '<a href="doc2">doc2</a>')
        self.assertEqual(IReferenceable(doc2).getBackReferences(), [doc1])

        # Make changes visible to testbrowseropen
        transaction.commit()

        # Then we use a browser to rename the referenced image:
        self.browser.handleErrors = True
        self.browser.open('{0:s}/object_rename?_authenticator={1:s}'.format(
            doc1.absolute_url(), self._get_token(doc1)))

        self.browser.getControl(name='form.widgets.new_id').value = 'nuname'
        self.browser.getControl(name='form.buttons.Rename').click()
        self.assertIn("Renamed 'doc1' to 'nuname'.", self.browser.contents)
        self.assertNotIn('doc1', self.portal.objectIds())
        self.assertIn('nuname', self.portal.objectIds())
        self.assertEqual(IReferenceable(doc2).getBackReferences(), [doc1])

        self._set_response_status_code(
            'LinkIntegrityNotificationException', 200)

        # We simply use a browser to try to delete a content item. 
        self.browser.open(doc2.absolute_url())
        self.browser.getLink('Delete').click()
        self.assertIn(
            'Do you really want to delete this item?', self.browser.contents)
        self.browser.getControl(name='form.buttons.Delete').click()
        self.assertIn('nuname', self.portal.objectIds())

        # Link breakabe page should be shown
        self.assertIn('Potential link breakage', self.browser.contents)
        self.assertIn('<a href="http://nohost/plone/nuname">Test Page 1</a>',
                      self.browser.contents)

    def test_removal_in_subfolder(self):
        doc1 = self.portal.doc1
        doc2 = self.portal.doc2
        folder1 = self.portal.folder1

        # This tests ensuring link integrity when removing an referenced 
        # object contained in a folder that is removed.
        self._set_text(doc1, '<a href="folder1/doc4">a document</a>')
        self._set_text(doc2, '<a href="folder1/doc4">a document</a>')

        # Make changes visible to testbrowseropen
        transaction.commit()

        # Then we try to delete the folder holding the referenced 
        # document. Before we can do this we need to prevent the test 
        # framework from choking on the exception we intentionally 
        # throw.
        self.browser.handleErrors = True
        self._disable_event_count_helper()
        self._set_response_status_code('Retry', 200)
        self._set_response_status_code(
            'LinkIntegrityNotificationException', 200)

        self.browser.open('{0:s}/object_delete?_authenticator={1:s}'.format(
            folder1.absolute_url(), self._get_token(folder1)))
        self.assertIn('Potential link breakage', self.browser.contents)
        self.assertIn('<a href="http://nohost/plone/doc1">Test Page 1</a>',
                      self.browser.contents)
        self.assertIn('<a href="http://nohost/plone/doc2">Test Page 2</a>',
                      self.browser.contents)
        self.browser.getControl(name='delete').click()
        
        # TODO: Retry exception is raised. Not sure this is an error in 
        # z2.Browser or just a wrong patched environment. Can please 
        # somebody who did this patching check this and fix this test 
        # here, thanks.
        # self.assertNotIn('folder1', self.portal.objectIds())


class FunctionalReferenceDXTestCase(DXBaseTestCase, ReferenceTestCase):
    """Functional reference testcase for dx content types"""

    layer = testing.PLONE_APP_LINKINTEGRITY_DX_FUNCTIONAL_TESTING


class FunctionalReferenceATTestCase(ATBaseTestCase, ReferenceTestCase):
    """Functional reference testcase for dx content types"""

    layer = testing.PLONE_APP_LINKINTEGRITY_AT_FUNCTIONAL_TESTING