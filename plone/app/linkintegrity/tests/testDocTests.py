# setup tests with all doctests found in docs/

from plone.app.linkintegrity import docs
from Testing.ZopeTestCase import FunctionalDocFileSuite
from Products.PloneTestCase import PloneTestCase
from Products.Five.testbrowser import Browser
from unittest import TestSuite
from StringIO import StringIO
from base64 import decodestring
from os.path import join, abspath, dirname
from os import walk


PloneTestCase.setupPloneSite()

from ZPublisher.HTTPRequest import HTTPRequest
set_orig = HTTPRequest.set

class LinkIntegrityFunctionalTestCase(PloneTestCase.FunctionalTestCase):
    
    def afterSetUp(self):
        """ create some sample content to test with """
        gif = 'R0lGODlhAQABAPAAAPj8+AAAACH5BAEAAAAALAAAAAABAAEAAAICRAEAOw=='
        gif = StringIO(decodestring(gif))
        self.loginAsPortalOwner()
        self.portal.invokeFactory('Document', id='doc1', title='Test Page 1',
            text='<html> <body> a test page </body> </html>')
        self.portal.invokeFactory('Document', id='doc2', title='Test Page 2',
            text='<html> <body> another test page </body> </html>')
        self.portal.invokeFactory('Image', id='image1', title='Test Image 1', image=gif)
        self.portal.invokeFactory('Image', id='image2', title='Test Image 2', image=gif)
        self.portal.invokeFactory('Image', id='image3', title='Test Image 3', image=gif)
        self.portal.invokeFactory('Folder', id='folder1', title='Test Folder 1')
        self.portal.folder1.invokeFactory('Document', id='doc3', title='Test Page 3',
            text='<html> <body> a test page in a subfolder </body> </html>')
        self.portal.folder1.invokeFactory('Document', id='doc4', title='Test Page 4',
            text='<html> <body> another test page </body> </html>')
        self.portal.folder1.invokeFactory('Document', id='doc5', title='Test Page 5',
            text='<html> <body> another test page </body> </html>')
        self.login()
        # HTTPRequest's 'set' function is set to it's original implementation
        # at the start of each new test, since otherwise the below monkey
        # patch will apply to all remaining tests (and break them);  see
        # comment below in 'disableEventCountHelper'
        HTTPRequest.set = set_orig
    
    def getBrowser(self, loggedIn=False):
        """ instantiate and return a testbrowser for convenience """
        browser = Browser()
        if loggedIn:
            user = PloneTestCase.default_user
            pwd = PloneTestCase.default_password
            browser.addHeader('Authorization', 'Basic %s:%s' % (user, pwd))
        return browser
    
    def setStatusCode(self, key, value):
        from ZPublisher import HTTPResponse
        HTTPResponse.status_codes[key.lower()] = value
    
    def disableEventCountHelper(self):
        # so here's yet another monkey patch ;), but only to avoid having
        # to change almost all the tests after introducing the setting of
        # the helper value in 'folder_delete', which prevents presenting
        # the user with multiple confirmation forms;  this patch prevents
        # setting the value and is meant to disable this optimization in
        # some of the tests written so far, thereby not invalidating them...
        def set(self, key, value, set_orig=set_orig):
            if key == 'link_integrity_events_to_expect':
                value = 0
            set_orig(self, key, value)
        HTTPRequest.set = set
    

def test_suite():
    suite = TestSuite()
    docs_dir = abspath(dirname(docs.__file__)) + '/'
    for path, dirs, files in walk(docs_dir):
        for name in files:
            relative = join(path, name)[len(docs_dir):]
            if name.startswith('test') and name.endswith('.txt'):
                suite.addTest(FunctionalDocFileSuite(relative,
                    package=docs.__name__,
                    test_class=LinkIntegrityFunctionalTestCase))
    return suite


