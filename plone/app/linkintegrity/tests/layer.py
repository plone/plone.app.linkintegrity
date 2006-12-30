from Products.PloneTestCase import five
from Products.PloneTestCase import setup

class PloneLinkintegrity:

    def setUp(cls):
        '''Sets up the Plone site(s).'''
        five.safe_load_site()
        setup.deferredSetup()
    setUp = classmethod(setUp)

    def tearDown(cls):
        '''Removes the Plone site(s).'''
        setup.cleanUp()
        five.cleanUp()
    tearDown = classmethod(tearDown)
