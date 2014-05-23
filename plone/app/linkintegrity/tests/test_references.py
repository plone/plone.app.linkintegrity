from Products.PloneTestCase import PloneTestCase
from plone.app.linkintegrity.tests.utils import getBrowser
from Products.Five.browser import BrowserView
from zope.component import provideAdapter
from zope.interface import implementer
from zope.interface import Interface
from zope.publisher.interfaces import IPublishTraverse
from zope.publisher.interfaces.browser import IHTTPRequest
from zope.publisher.interfaces.browser import IBrowserView

PloneTestCase.setupPloneSite()


@implementer(IPublishTraverse)
class MyTraversingView(BrowserView):

    def __call__(self):        
        return self.subpath

    def publishTraverse(self, request, name):
        if not hasattr(self, 'subpath'):
            self.subpath = []
        self.subpath.append(name)
        return self


class ReferenceGenerationTests(PloneTestCase.FunctionalTestCase):
    
    def setUp(self):
        super(ReferenceGenerationTests, self).setUp()
        provideAdapter(
                MyTraversingView,
                (Interface,
                 IHTTPRequest),
                 provides=IBrowserView,
                name=u'foo-view'
            )

    def testRelativeUpwardsLinkGeneratesMatchingReference(self):
        self.setRoles(['Manager'])
        portal = self.portal
        portal.invokeFactory('Document', id='foo', text='main foo!')
        folder = portal[portal.invokeFactory('Folder', id='folder')]
        folder.invokeFactory('Document', id='foo', text='sub foo?')
        doc = folder[folder.invokeFactory('Document', id='doc',
            text='<html> <body> <a href="../foo">go!</a> </body> </html>')]
        # the way relative links work it leads to the main 'foo'...
        browser = getBrowser(loggedIn=True)
        browser.open(doc.absolute_url())
        browser.getLink('go!').click()
        self.assertTrue('main foo' in browser.contents)
        # the internal reference should do the same...
        self.assertEqual(doc.getReferences(), [portal.foo])

    def testRelativeSiblingFolderLinkGeneratesMatchingReference(self):
        self.setRoles(['Manager'])
        portal = self.portal
        main = portal[portal.invokeFactory('Folder', id='main')]
        foo = main[main.invokeFactory('Folder', id='foo')]
        foo.invokeFactory('Document', id='doc', text='dox rule!')
        bar = main[main.invokeFactory('Folder', id='bar')]
        doc = bar[bar.invokeFactory('Document', id='doc',
            text='<html> <body> <a href="../foo/doc">go!</a> </body> </html>')]
        # the way relative links work it leads to the document in folder 'foo'
        browser = getBrowser(loggedIn=True)
        browser.open(doc.absolute_url())
        browser.getLink('go!').click()
        self.assertTrue('dox rule' in browser.contents)
        # the internal reference should do the same...
        self.assertEqual(doc.getReferences(), [portal.main.foo.doc])

    def testReferencesToNonAccessibleContentAreGenerated(self):
        self.loginAsPortalOwner()
        secret = self.portal[self.portal.invokeFactory('Document', id='secret')]
        self.login()
        # somebody created a document to which the user has no access...
        checkPermission = self.portal.portal_membership.checkPermission
        self.assertFalse(checkPermission('View', secret))
        self.assertFalse(checkPermission('Access contents information', secret))
        # nevertheless it should be possible to set a link to it...
        self.folder.invokeFactory('Document', id='doc',
            text='<html> <body> <a href="%s">go!</a> </body> </html>' %
            secret.absolute_url())
        self.assertEqual(self.folder.doc.getReferences(), [secret])

    def testReferencesToFSPythonScriptAreGenerated(self):
        self.loginAsPortalOwner()
        self.portal.invokeFactory('File', id='attachment', file='foo bar')
        self.portal.invokeFactory('Document', id='foo',
                                  text='<p><a href="attachment/at_download/whatever">go!</a></p>')
        self.assertEqual(self.portal.foo.getReferences(), [self.portal.attachment])

    def testReferencesToViewAreGenerated(self):
        self.loginAsPortalOwner()
        self.portal.invokeFactory('File', id='attachment', file='foo bar')
        self.portal.invokeFactory('Document', id='foo',
                                  text='<p><a href="attachment/@@foo-view/something">go!</a></p>')
        self.assertEqual(self.portal.foo.getReferences(), [self.portal.attachment])
