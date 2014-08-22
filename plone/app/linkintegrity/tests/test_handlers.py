from Products.PloneTestCase import PloneTestCase
from plone.app.linkintegrity.handlers import findObject

PloneTestCase.setupPloneSite()


class FindObjectTests(PloneTestCase.PloneTestCase):
    """ testing the handlers.findObject function """
    
    def afterSetUp(self):
        """ create some sample content to test with """
        self.setRoles(('Manager',))
        self.portal.invokeFactory(type_name='Document', id='doc1')
        self.portal.invokeFactory(type_name='Document', id='doc2')

    def test_relative_to_portal_root_1(self):
        obj, components = findObject(self.portal.doc1, '/plone/doc2')
        self.assertEqual(obj.absolute_url_path(), '/plone/doc2')
        self.assertEqual(components, '')

    def test_relative_to_portal_root_2(self):
        # Prevent regression. See https://github.com/plone/plone.app.linkintegrity/pull/17
        obj, components = findObject(self.portal.doc1, '/doc2')
        self.assertEqual(obj.absolute_url_path(), '/plone/doc2')
        self.assertEqual(components, '')
