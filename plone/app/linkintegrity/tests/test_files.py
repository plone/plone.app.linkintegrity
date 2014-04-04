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


class FileReferenceTests:

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
        _response = self.request.response
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

        self.request.response = _response



class FileReferenceDXTests(DXBaseTestCase, FileReferenceTests):
    """File reference testcase for dx content types"""


class FileReferenceATTests(ATBaseTestCase, FileReferenceTests):
    """File reference testcase for dx content types"""
