# -*- coding: utf-8 -*-
from Products.Archetypes.interfaces import IReferenceable
from plone.app.linkintegrity import testing
from plone.app.linkintegrity import exceptions
from plone.app.linkintegrity.tests.base import ATBaseTestCase
from plone.app.linkintegrity.tests.base import DXBaseTestCase


class FileReferenceTests:

    def test_file_reference(self):
        """This tests the behaviour when removing a referenced file."""

        doc1 = self.portal.doc1
        afile = testing.create(self.portal, 'File', id='a-file')

        self._set_text(doc1, '<a href="a-file">A File</a>')
        self.assertEqual(IReferenceable(doc1).getReferences(), [afile])

        token = self._get_token(afile)
        self.request['_authenticator'] = token

        # Throws exception
        view = afile.restrictedTraverse('@@object_delete')
        self.assertRaises(exceptions.LinkIntegrityNotificationException, view)


class FileReferenceDXTests(DXBaseTestCase, FileReferenceTests):
    """ """


class FileReferenceATTests(ATBaseTestCase, FileReferenceTests):
    """ """
