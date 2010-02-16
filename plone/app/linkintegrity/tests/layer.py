from Testing.ZopeTestCase import installPackage
from Products.Five import zcml, fiveconfigure
from collective.testcaselayer.ptc import BasePTCLayer, ptc_layer
from StringIO import StringIO
from base64 import decodestring


class PloneLinkintegrity(BasePTCLayer):

    def afterSetUp(self):
        # load zcml for this package...
        fiveconfigure.debug_mode = True
        from plone.app import linkintegrity
        zcml.load_config('configure.zcml', package=linkintegrity)
        fiveconfigure.debug_mode = False
        # after which it can be initialized...
        installPackage('plone.app.linkintegrity', quiet=True)

        # create sample content
        self.loginAsPortalOwner()
        gif = 'R0lGODlhAQABAPAAAPj8+AAAACH5BAEAAAAALAAAAAABAAEAAAICRAEAOw=='
        gif = StringIO(decodestring(gif))
        portal = self.portal
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

        # Unmark the creation flag so any calls processForm/setText will not
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
        self.login()


integrity = PloneLinkintegrity(bases=[ptc_layer])
