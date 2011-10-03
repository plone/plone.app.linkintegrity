from Products.PloneTestCase import PloneTestCase
from plone.app.linkintegrity.tests import layer


PloneTestCase.setupPloneSite()


class PasteTestCase(PloneTestCase.PloneTestCase):

    layer = layer.integrity

    def test_can_paste(self):
        self.setRoles(('Manager',))
        cp = self.portal.manage_copyObjects(['doc1'])
        import transaction
        transaction.savepoint()
        self.portal.manage_pasteObjects(cp)
