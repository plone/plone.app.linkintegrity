# -*- coding: utf-8 -*-
from Products.Archetypes.interfaces import IBaseObject
from Products.CMFCore.utils import getToolByName
from base64 import decodestring
from StringIO import StringIO
from plone.app.contenttypes.testing import (
    PLONE_APP_CONTENTTYPES_FIXTURE,
    PLONE_APP_CONTENTTYPES_MIGRATION_FIXTURE
)
from plone.app.testing import PLONE_FIXTURE
from plone.app.testing import TEST_USER_ID
from plone.app.testing import TEST_USER_NAME
from plone.app.testing import TEST_USER_PASSWORD
from plone.app.testing import applyProfile
from plone.app.testing import layers
from plone.app.testing import login
from plone.app.testing import ploneSite
from plone.app.testing import setRoles
from plone.testing import z2
from zope.configuration import xmlconfig

GIF = StringIO(decodestring(
    'R0lGODlhAQABAPAAAPj8+AAAACH5BAEAAAAALAAAAAABAAEAAAICRAEAOw=='))


def create(container, type_name, **kwargs):
    """A easy helper method to create some content since we do not have
       plone.api in core.
    """

    new_id = container.invokeFactory(type_name, **kwargs)
    content = container[new_id]

    # Archetypes specific code was taken from ``plone.api``
    # Switch when api has been merged into core.
    if IBaseObject.providedBy(content):
        content.processForm()

    return content


class LinkIntegrityLayer(z2.Layer):
    """Base Layer for AT and Dexterity testing"""

    defaultBases = (PLONE_FIXTURE, )

    def setUpMembers(self, portal):
        pm = getToolByName(portal, 'portal_membership')
        pm.addMember('editor', TEST_USER_PASSWORD, ['Editor'], [])
        pm.addMember('member', TEST_USER_PASSWORD, ['Member'], [])
        pm.addMember('authenticated', TEST_USER_PASSWORD, [], [])

    def setUpContent(self):
        import plone.app.linkintegrity

        xmlconfig.file('configure.zcml', plone.app.linkintegrity,
                       context=self['configurationContext'])

        with ploneSite() as portal:
            setRoles(portal, TEST_USER_ID, ['Manager', ])
            login(portal, TEST_USER_NAME)

            # Create sample documents
            type_data = dict(type_name='Document')
            for i in range(1, 4):
                type_data['id'] = 'doc{0:d}'.format(i)
                type_data['title'] = 'Test Page {0:d}'.format(i)
                create(portal, **type_data)

            type_data = dict(type_name='Image', image=GIF)
            for i in range(1, 3):
                type_data['id'] = 'image{0:d}'.format(i)
                type_data['title'] = 'Test Image {0:d}'.format(i)
                create(portal, **type_data)

            create(portal, 'Folder', id='folder1', title='Test Folder 1')
            create(portal, 'File', id='file1', title='Test File 1', file=GIF)

            type_data = dict(type_name='Document')
            for i in range(4, 6):
                type_data['id'] = 'doc{0:d}'.format(i)
                type_data['title'] = 'Test Page {0:d}'.format(i)
                create(portal['folder1'], **type_data)

            self.setUpMembers(portal)

PLONE_APP_LINKINTEGRITY_FIXTURE = LinkIntegrityLayer()


class LinkIntegrityATLayer(LinkIntegrityLayer):
    """Layer which targets testing with Archetypes and ATContentTypes"""

    directory = 'at'
    defaultBases = (
        PLONE_APP_CONTENTTYPES_MIGRATION_FIXTURE,
        PLONE_APP_LINKINTEGRITY_FIXTURE,
    )

    def setUp(self):
        self.setUpContent()

PLONE_APP_LINKINTEGRITY_AT_FIXTURE = LinkIntegrityATLayer()


class LinkIntegrityDXLayer(LinkIntegrityLayer):
    """Layer which targets testing with Dexterity"""

    directory = 'dx'
    defaultBases = (
        PLONE_APP_CONTENTTYPES_FIXTURE,
        PLONE_APP_LINKINTEGRITY_FIXTURE,
    )
    types_providing_referencable_behavior = set([
        'Folder',
        'Image',
        'Document',
    ])

    def setUp(self):
        with ploneSite() as portal:
            ttool = getToolByName(portal, 'portal_types')
            for type_info in self.types_providing_referencable_behavior:
                ttool.getTypeInfo(type_info).behaviors += (
                    'plone.app.referenceablebehavior.referenceable.IReferenceable',  # noqa
                )

            # FIXME: we need uid_catalog and referencer_catalog to keep
            #        plone.app.referencebehavior working. So load Archetypes
            #        profile to install those tools before we continue
            applyProfile(portal, 'Products.Archetypes:Archetypes')

        self.setUpContent()


PLONE_APP_LINKINTEGRITY_DX_FIXTURE = LinkIntegrityDXLayer()

PLONE_APP_LINKINTEGRITY_AT_INTEGRATION_TESTING = layers.IntegrationTesting(
    bases=(PLONE_APP_LINKINTEGRITY_AT_FIXTURE, ),
    name='plone.app.linkintegrity:AT:Integration'
)

PLONE_APP_LINKINTEGRITY_DX_INTEGRATION_TESTING = layers.IntegrationTesting(
    bases=(PLONE_APP_LINKINTEGRITY_DX_FIXTURE, ),
    name='plone.app.linkintegrity:DX:Integration'
)

PLONE_APP_LINKINTEGRITY_AT_FUNCTIONAL_TESTING = layers.FunctionalTesting(
    bases=(PLONE_APP_LINKINTEGRITY_AT_FIXTURE, ),
    name='plone.app.linkintegrity:AT:Functional'
)
PLONE_APP_LINKINTEGRITY_DX_FUNCTIONAL_TESTING = layers.FunctionalTesting(
    bases=(PLONE_APP_LINKINTEGRITY_DX_FIXTURE, ),
    name='plone.app.linkintegrity:DX:Functional'
)
