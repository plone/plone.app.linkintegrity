from Products.PloneTestCase import PloneTestCase
from plone.app.linkintegrity.tests.utils import getBrowser


PloneTestCase.setupPloneSite()


class ReferenceGenerationTests(PloneTestCase.FunctionalTestCase):

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
