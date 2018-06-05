# -*- coding: utf-8 -*-
from plone.app.linkintegrity import testing
from plone.app.linkintegrity.tests.base import DXBaseTestCase
# from plone.app.linkintegrity.utils import hasIncomingLinks
from plone.app.linkintegrity.utils import getIncomingLinks
from plone.app.linkintegrity.utils import getOutgoingLinks
from plone.app.linkintegrity.utils import hasOutgoingLinks
from plone.app.testing import TEST_USER_NAME
from plone.app.testing import TEST_USER_PASSWORD
from plone.registry.interfaces import IRegistry
from plone.testing.z2 import Browser
from Products.CMFPlone.interfaces import IEditingSchema
from zc.relation.interfaces import ICatalog
from zope.component import getUtility

import six
import transaction
import unittest


class ReferenceTestCase:

    @unittest.skip('Re-enable after https://github.com/plone/plone.app.content/issues/38')  # noqa
    def test_file_reference_linkintegrity_page_is_shown(self):
        doc1 = self.portal.doc1
        file2 = testing.create(self.portal, 'File',
                               id='file2', file=testing.GIF)

        self.assertFalse(hasOutgoingLinks(doc1))
        self._set_text(doc1, '<a href="file2">A File</a>')
        self.assertTrue(hasOutgoingLinks(doc1))
        self.assertIn('file2', self.portal.objectIds())

        token = self._get_token(file2)
        self.request['_authenticator'] = token

        # Make changes visible to test browser
        transaction.commit()

        self.browser.handleErrors = True
        self.browser.addHeader(
            'Authorization',
            'Basic {0:s}:{1:s}'.format(TEST_USER_NAME, TEST_USER_PASSWORD))

        delete_url = '{0:s}/delete_confirmation?_authenticator={1:s}'.format(
            file2.absolute_url(), token)

        # Try to remove but cancel
        self.browser.open(delete_url)

        # Validate text
        self.assertIn('Potential link breakage', self.browser.contents)
        self.assertIn('<a href="http://nohost/plone/doc1">Test Page 1</a>',
                      self.browser.contents)
        self.assertIn('Would you like to delete it anyway?',
                      self.browser.contents)

        # Click cancel button, item should stay in place
        # FIXME! This fails in Archetypes because the redirect
        # plone.app.content.browser.actions.DeleteConfirmationForm.handle_cancel
        # is broken for AT-content.
        self.browser.getControl(name='form.buttons.Cancel').click()
        self.assertEqual(self.browser.url, file2.absolute_url() + '/view')
        self.assertIn('Removal cancelled.', self.browser.contents)
        self.assertIn('file2', self.portal.objectIds())

        # Try to remove and confirm
        self.browser.open(delete_url)
        self.browser.getControl(name='form.buttons.Delete').click()
        self.assertNotIn('file2', self.portal.objectIds())

    def test_unreferenced_removal(self):
        # This tests against #6666 and #7784, simple removal of a not
        # referenced file, which broke zeo-based installations.

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
        self.assertEqual(
            [i.from_object for i in getIncomingLinks(doc2)], [doc1])

        # Make changes visible to testbrowseropen
        transaction.commit()

        # Then we use a browser to rename the referenced image:
        self.browser.handleErrors = True
        self.browser.open('{0:s}/object_rename?_authenticator={1:s}'.format(
            doc1.absolute_url(), self._get_token(doc1)))

        self.browser.getControl(name='form.widgets.new_id').value = 'nuname'
        self.browser.getControl(name='form.buttons.Rename').click()
        self.assertIn("Renamed 'doc1' to 'nuname'.", self.browser.contents)
        transaction.commit()

        self.assertNotIn('doc1', self.portal.objectIds())
        self.assertIn('nuname', self.portal.objectIds())
        self.assertIn(doc1, [i.from_object for i in getIncomingLinks(doc2)])

        # We simply use a browser to try to delete a content item.
        self.browser.open(doc2.absolute_url())
        self.browser.getLink('Delete').click()
        self.assertIn(
            'Do you really want to delete this item?', self.browser.contents)
        self.assertIn('nuname', self.portal.objectIds())
        # Link breakabe page should be shown
        self.assertIn('Potential link breakage', self.browser.contents)
        self.assertIn('<a href="http://nohost/plone/nuname">Test Page 1</a>',
                      self.browser.contents)
        self.browser.getControl(name='form.buttons.Delete').click()
        self.assertNotIn('doc2', self.portal.objectIds())

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

        self.browser.open(
            '{0:s}/delete_confirmation?_authenticator={1:s}'.format(
                folder1.absolute_url(), self._get_token(folder1)
            )
        )
        self.assertIn('Potential link breakage', self.browser.contents)
        self.assertIn('<a href="http://nohost/plone/doc1">Test Page 1</a>',
                      self.browser.contents)
        self.assertIn('<a href="http://nohost/plone/doc2">Test Page 2</a>',
                      self.browser.contents)
        self.browser.getControl(name='form.buttons.Delete').click()
        self.assertNotIn('folder1', self.portal.objectIds())

    def test_removal_with_cookie_auth(self):
        doc1 = self.portal.doc1
        doc2 = self.portal.doc2

        # This tests ensures link integrity working correctly without
        # http basic authentication (see the bug report in #6607).
        self._set_text(doc1, '<a href="doc2">doc2</a>')
        transaction.commit()

        browser = Browser(self.layer['app'])
        browser.handleErrors = True
        browser.addHeader('Referer', self.portal.absolute_url())
        browser.open(
            '{0:s}/folder_contents'.format(self.portal.absolute_url()))

        # At this point we shouldn't be able to look at the folder
        # contents (as an anonymous user):
        self.assertIn('login?came_from', browser.url)

        # So we log in via the regular plone login form and additionally check
        # that there is no 'authorization' header set afterwards:
        browser.getControl(name='__ac_name').value = TEST_USER_NAME
        browser.getControl(name='__ac_password').value = TEST_USER_PASSWORD
        browser.getControl('Log in').click()
        self.assertNotIn(
            'authorization', [h.lower() for h in browser.headers.keys()])

        # This should lead us back to the "folder contents" listing,
        # where we try to delete the referenced document.
        browser.open('{0:s}/delete_confirmation?_authenticator={1:s}'.format(
            doc2.absolute_url(), self._get_token(doc2)))
        self.assertIn('Potential link breakage', browser.contents)
        self.assertIn('<a href="http://nohost/plone/doc1">Test Page 1</a>',
                      browser.contents)
        browser.getControl(name='form.buttons.Delete').click()
        self.assertNotIn('doc2', self.portal.objectIds())

    def test_linkintegrity_on_off_switch(self):
        doc1 = self.portal.doc1
        doc2 = self.portal.doc2

        # This tests switching link integrity checking on and off.
        self._set_text(doc1, '<a href="doc2">a document</a>')
        transaction.commit()

        # This should lead us back to the "folder contents" listing,
        # where we try to delete the referenced document. Before we can
        # do this we need to prevent the test framework from choking on
        # the exception we intentionally throw.
        self.browser.handleErrors = True

        self.browser.open(
            '{0:s}/delete_confirmation?_authenticator={1:s}'.format(
                doc2.absolute_url(), self._get_token(doc2)
            )
        )
        self.assertIn('Potential link breakage', self.browser.contents)
        self.assertIn('<a href="http://nohost/plone/doc1">Test Page 1</a>',
                      self.browser.contents)

        # Now we turn the switch for link integrity checking off via the site
        # properties and try again:
        registry = getUtility(IRegistry)
        settings = registry.forInterface(IEditingSchema, prefix='plone')
        settings.enable_link_integrity_checks = False
        transaction.commit()
        self.browser.reload()
        self.assertNotIn('Potential link breakage', self.browser.contents)

    def test_update(self):
        doc1 = self.portal.doc1
        doc2 = self.portal.doc2
        doc4 = self.portal.folder1.doc4

        # This tests updating link integrity information for all site content,
        # i.e. after migrating from a previous version.
        self._set_text(doc1, '<a href="doc2">a document</a>')
        self._set_text(doc2, '<a href="folder1/doc4">a document</a>')

        catalog = getUtility(ICatalog)
        rels = [i for i in catalog.findRelations()]
        for rel in rels:
            catalog.unindex(rel)

        # Just to make sure, we check that there are no references from or to
        # these documents at this point:
        self.assertEqual([i.to_object for i in getOutgoingLinks(doc1)], [])
        self.assertEqual([i.to_object for i in getOutgoingLinks(doc2)], [])

        # An update of link integrity information for all content is triggered
        # by browsing a specific url:
        transaction.commit()
        self.browser.open('{0:s}/updateLinkIntegrityInformation'.format(
            self.portal.absolute_url()))
        self.browser.getControl('Update').click()
        self.assertIn('Link integrity information updated for',
                      self.browser.contents)

        # Now the linking documents should hold the correct link integrity
        # references:
        self.assertEqual(
            [i.to_object for i in getOutgoingLinks(doc1)],
            [doc2, ],
        )
        self.assertEqual(
            [i.to_object for i in getOutgoingLinks(doc2)],
            [doc4, ],
        )

    def test_references_on_cloned_objects(self):
        doc1 = self.portal.doc1
        doc2 = self.portal.doc2

        # This tests ensures that link integrity is correctly setup when
        # cloning an object.
        self._set_text(doc1, '<a href="doc2">a document</a>')

        # Next we clone the document:
        token = self._get_token(doc1)
        self.request['_authenticator'] = token
        doc1.restrictedTraverse('object_copy')()

        self.request['_authenticator'] = token
        self.portal.restrictedTraverse('object_paste')()
        self.assertIn('copy_of_doc1', self.portal)
        transaction.commit()

        # Then we try to delete the document linked by the original document
        # and its clone. Before we can do this we need to prevent the test
        # framework from choking on the exception we intentionally throw.
        self.browser.handleErrors = True

        # Now we can continue and "click" the "delete" action. The confirmation
        # page should list both documents:
        self.browser.open(
            '{0:s}/delete_confirmation?_authenticator={1:s}'.format(
                doc2.absolute_url(), self._get_token(doc2)
            )
        )
        self.assertIn(
            'is referenced by the following items:', self.browser.contents)
        self.assertIn('Potential link breakage', self.browser.contents)
        self.assertIn(
            '<a href="http://nohost/plone/doc1">Test Page 1</a>',
            self.browser.contents
        )
        self.assertIn(
            '<a href="http://nohost/plone/copy_of_doc1"',
            self.browser.contents
        )

    def test_files_with_spaces_removal(self):
        doc1 = self.portal.doc1

        # This tests the behaviour when removing a referenced file that has
        # spaces in its id.  First we need to rename the existing file:
        self.portal.invokeFactory(
            'Document', id='some spaces.doc', title='A spaces doc')

        self.assertIn('some spaces.doc', self.portal.objectIds())
        spaces1 = self.portal['some spaces.doc']

        self._set_text(doc1, '<a href="some spaces.doc">a document</a>')

        # The document should now have a reference to the file:
        self.assertEqual(
            [i.to_object for i in getOutgoingLinks(doc1)], [spaces1])
        transaction.commit()

        # Then we use a browser to try to delete the referenced file.
        # Before we can do this we need to prevent the test framework
        # from choking on the exception we intentionally throw.
        self.browser.handleErrors = True

        self.browser.open(
            '{0:s}/delete_confirmation?_authenticator={1:s}'.format(
                spaces1.absolute_url(), self._get_token(spaces1)
            )
        )
        self.assertIn('Potential link breakage', self.browser.contents)
        self.assertIn(
            '<a href="http://nohost/plone/doc1">Test Page 1</a>',
            self.browser.contents
        )
        self.browser.getControl(name='form.buttons.Delete').click()
        self.assertNotIn('some spaces.doc', self.portal.objectIds())

    def test_removal_via_zmi(self):
        """Delete via ZMI is no longer protedted!"""
        doc1 = self.portal.doc1
        doc2 = self.portal.doc2

        # This tests ensuring link integrity when removing an object via
        # the ZMI.
        self._set_text(doc1, '<a href="doc2">a document</a>')
        self.assertEqual([i.to_object for i in getOutgoingLinks(doc1)], [doc2])

        transaction.commit()
        # Then we use a browser to try to delete the referenced
        # document. Before we can do this we need to prevent the test
        # framework from choking on the exception we intentionally throw.
        self.browser.handleErrors = True

        self.browser.open('http://nohost/plone/manage_main')
        self.browser\
            .getControl(name='ids:list')\
            .getControl(value='doc2').selected = True

        self.browser.getControl('Delete').click()
        self.assertNotIn('doc2', self.portal.objectIds())

    def test_warn_about_content(self):
        folder1 = self.portal.folder1
        self.browser.open(
            '{0:s}/delete_confirmation?_authenticator={1:s}'.format(
                folder1.absolute_url(), self._get_token(folder1)
            )
        )
        self.assertIn('Number of selected', self.browser.contents)
        self.assertIn('2 Objects in all', self.browser.contents)
        self.assertIn('1 Folders', self.browser.contents)
        self.assertIn('0 Published objects', self.browser.contents)


class FunctionalReferenceDXTestCase(DXBaseTestCase, ReferenceTestCase):
    """Functional reference testcase for dx content types"""

    layer = testing.PLONE_APP_LINKINTEGRITY_DX_FUNCTIONAL_TESTING


if six.PY2:
    from plone.app.linkintegrity.tests.base import ATBaseTestCase

    class FunctionalReferenceATTestCase(ATBaseTestCase, ReferenceTestCase):
        """Functional reference testcase for dx content types"""

        layer = testing.PLONE_APP_LINKINTEGRITY_AT_FUNCTIONAL_TESTING
