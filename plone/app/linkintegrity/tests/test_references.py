# -*- coding: utf-8 -*-
from zope.event import notify
from zope.lifecycleevent import ObjectModifiedEvent
from plone.app.referenceablebehavior.referenceable import IReferenceable

from plone.app.testing import setRoles
from plone.app.testing import logout
from plone.app.testing import login
from plone.app.testing import TEST_USER_ID
from plone.app.testing import TEST_USER_NAME
from plone.app.testing import TEST_USER_PASSWORD
from plone.app.linkintegrity.testing import (
    PLONE_APP_LINKINTEGRITY_AT_INTEGRATION_TESTING,
    PLONE_APP_LINKINTEGRITY_DX_INTEGRATION_TESTING
)
from plone.testing.z2 import Browser

import unittest

@unittest.skip("DX is broken anyway")
class ReferenceGenerationDXTests(unittest.TestCase):

    layer = PLONE_APP_LINKINTEGRITY_DX_INTEGRATION_TESTING

    def setUp(self):
        self.portal = self.layer['portal']
        self.browser = Browser(self.layer['app'])
        self.browser.handleErrors = False
        self.browser.addHeader(
            'Authorization',
            'Basic {0:s}:{1:s}'.format(TEST_USER_NAME, TEST_USER_PASSWORD))

        setRoles(self.portal, TEST_USER_ID, ['Manager', ])

    def testRelativeUpwardsLinkGeneratesMatchingReference(self):
        portal = self.portal
        portal.invokeFactory('Document', id='foo', text='main foo!')
        folder = portal[portal.invokeFactory('Folder', id='folder')]
        folder.invokeFactory('Document', id='foo', text='sub foo?')
        doc = folder[folder.invokeFactory('Document', id='doc',
            text='<html> <body> <a href="../foo">go!</a> </body> </html>')]
        # the way relative links work it leads to the main 'foo'...
        self.browser.open(doc.absolute_url())
        self.browser.getLink('go!').click()
        self.assertTrue('main foo' in self.browser.contents)
        # the internal reference should do the same...
        self.assertEqual(doc.getReferences(), [portal.foo])

    def testRelativeSiblingFolderLinkGeneratesMatchingReference(self):
        setRoles(self.portal, TEST_USER_ID, ['Manager'])
        portal = self.portal
        main = portal[portal.invokeFactory('Folder', id='main')]
        foo = main[main.invokeFactory('Folder', id='foo')]
        foo.invokeFactory('Document', id='doc', text='dox rule!')
        bar = main[main.invokeFactory('Folder', id='bar')]
        doc = bar[bar.invokeFactory('Document', id='doc',
            text='<html> <body> <a href="../foo/doc">go!</a> </body> </html>')]
        # the way relative links work it leads to the document in folder 'foo'
        self.browser.open(doc.absolute_url())
        self.browser.getLink('go!').click()
        self.assertTrue('dox rule' in self.browser.contents)
        # the internal reference should do the same...
        self.assertEqual(doc.getReferences(), [portal.main.foo.doc])

    def testReferencesToNonAccessibleContentAreGenerated(self):
        setRoles(self.portal, TEST_USER_ID, ['Manager'])
        secret = self.portal[self.portal.invokeFactory('Document', id='secret')]
#        from_member = self.portal[self.portal.invokeFactory('Document', 
#                                                            id='member')]
        from plone.dexterity.utils import createContentInContainer
        from_member = createContentInContainer(self.portal, 'Document', title=u"From Member")
        from_member.manage_setLocalRoles('member', ['Contributor'])
        # somebody created a document to which the user has no access...
        checkPermission = self.portal.portal_membership.checkPermission
        logout()
        login(self.portal, 'member')
        self.assertFalse(checkPermission('View', secret))
        self.assertFalse(checkPermission('Access contents information', secret))

        # nevertheless it should be possible to set a link to it...
        from_member.text = '<html> <body> <a href="%s">go!</a> </body> </html>'\
            % secret.absolute_url()
        notify(ObjectModifiedEvent(from_member))
        self.assertEqual(IReferenceable(from_member).getReferences(), [secret])


class ReferenceGenerationATTests(ReferenceGenerationDXTests):

    layer = PLONE_APP_LINKINTEGRITY_AT_INTEGRATION_TESTING
