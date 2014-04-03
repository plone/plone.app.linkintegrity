# -*- coding: utf-8 -*-
from Products.Archetypes.interfaces import IReferenceable
from plone.app.linkintegrity import testing
from plone.app.linkintegrity import exceptions
from plone.app.linkintegrity.tests.base import ATBaseTestCase
from plone.app.linkintegrity.tests.base import DXBaseTestCase

import transaction


class FileReferenceTests:

    def test_file_reference(self):
        """This tests the behaviour when removing a referenced file."""

        doc1 = self.portal.doc1
        afile = testing.create(self.portal, 'File',
                               id='file2', file=testing.GIF)

        self._set_text(doc1, '<a href="file2">A File</a>')
        self.assertEqual(IReferenceable(doc1).getReferences(), [afile])
        self.assertIn('file2', self.portal.objectIds())

        token = self._get_token(afile)
        self.request['_authenticator'] = token

        # Throws exception which actually should abort transaction
        view = afile.restrictedTraverse('@@object_delete')
        self.assertRaises(exceptions.LinkIntegrityNotificationException, view)

    def test_file_reference_linkintegrity_page_is_shown(self):
        doc1 = self.portal.doc1
        afile = testing.create(self.portal, 'File',
                               id='file2', file=testing.GIF)

        self._set_text(doc1, '<a href="file2">A File</a>')
        self.assertEqual(IReferenceable(doc1).getReferences(), [afile])
        self.assertIn('file2', self.portal.objectIds())

        token = self._get_token(afile)
        self.request['_authenticator'] = token

        # Make changes visible to test browser
        transaction.commit()

        # TODO: Check confirmation page is shown in browser. Actually it
        #       fails because of a different than 200 response code.
        # self._set_response_status_code(
        #     'LinkIntegrityNotificationException', 200)

        # self.browser.open('{0:s}/object_delete?_authenticator={1:s}'.format(
        #     afile.absolute_url(), token))

        # self.browser.contents
        # import pdb; pdb.set_trace( )


class FileReferenceDXTests(DXBaseTestCase, FileReferenceTests):
    """ """


class FileReferenceATTests(ATBaseTestCase, FileReferenceTests):
    """ """
