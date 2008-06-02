from AccessControl.SecurityManagement import newSecurityManager
from Testing import ZopeTestCase
from Products.PloneTestCase import PloneTestCase
from Products.PloneTestCase.layer import PloneSite
from StringIO import StringIO
from base64 import decodestring
from transaction import commit


class PloneLinkintegrity(PloneSite):

    @classmethod
    def setUp(cls):
        app = ZopeTestCase.app()
        portal = app.plone

        # login as admin (copied from `loginAsPortalOwner`)
        uf = app.acl_users
        user = uf.getUserById(PloneTestCase.portal_owner).__of__(uf)
        newSecurityManager(None, user)

        # create sample content
        gif = 'R0lGODlhAQABAPAAAPj8+AAAACH5BAEAAAAALAAAAAABAAEAAAICRAEAOw=='
        gif = StringIO(decodestring(gif))
        portal.invokeFactory('Document', id='doc1', title='Test Page 1',
            text='<html> <body> a test page </body> </html>')
        portal.invokeFactory('Document', id='doc2', title='Test Page 2',
            text='<html> <body> another test page </body> </html>')
        portal.invokeFactory('Image', id='image1', title='Test Image 1', image=gif)
        portal.invokeFactory('Image', id='image2', title='Test Image 2', image=gif)
        portal.invokeFactory('Image', id='image3', title='Test Image 3', image=gif)
        portal.invokeFactory('File', id='file1', title='Test File 1', file=gif)
        portal.invokeFactory('Folder', id='folder1', title='Test Folder 1')
        portal.folder1.invokeFactory('Document', id='doc3', title='Test Page 3',
            text='<html> <body> a test page in a subfolder </body> </html>')
        portal.folder1.invokeFactory('Document', id='doc4', title='Test Page 4',
            text='<html> <body> another test page </body> </html>')
        portal.folder1.invokeFactory('Document', id='doc5', title='Test Page 5',
            text='<html> <body> another test page </body> </html>')

        # Unmark the creation flag so any calls processForm will not
        # rename our content objects.  This is mainly for getting the
        # tests running in combination with LinguaPlone.
        portal.doc1.unmarkCreationFlag()
        portal.doc2.unmarkCreationFlag()
        portal.image1.unmarkCreationFlag()
        portal.image2.unmarkCreationFlag()
        portal.image3.unmarkCreationFlag()
        portal.file1.unmarkCreationFlag()
        portal.folder1.unmarkCreationFlag()
        portal.folder1.doc3.unmarkCreationFlag()
        portal.folder1.doc4.unmarkCreationFlag()
        portal.folder1.doc5.unmarkCreationFlag()

        # starting with 2.10.4 product initialization gets delayed for
        # instance startup and is never called when running tests;  hence
        # we have to initialize the package method manually...
        from OFS.Application import install_package
        import plone.app.linkintegrity
        install_package(app, plone.app.linkintegrity, plone.app.linkintegrity.initialize)

        # create a starting point for the tests...
        commit()
        ZopeTestCase.close(app)

    @classmethod
    def tearDown(cls):
        app = ZopeTestCase.app()
        portal = app.plone

        # login as admin (copied from `loginAsPortalOwner`)
        uf = app.acl_users
        user = uf.getUserById(PloneTestCase.portal_owner).__of__(uf)
        newSecurityManager(None, user)

        # remove sample content
        ids = 'doc1', 'doc2', 'image1', 'image2', 'image3', 'folder1', 'file1'
        portal.manage_delObjects(ids=list(ids))

        # commit the cleanup...
        commit()
        ZopeTestCase.close(app)


