# -*- coding: utf-8 -*-
from Products.CMFCore.utils import getToolByName
from base64 import decodestring
from plone.app.contenttypes.testing import (
    PLONE_APP_CONTENTTYPES_FIXTURE,
    PLONE_APP_CONTENTTYPES_MIGRATION_FIXTURE
)
from plone.app.testing import PLONE_FIXTURE
from plone.app.testing import TEST_USER_ID
from plone.app.testing import TEST_USER_NAME
from plone.app.testing import layers
from plone.app.testing import login
from plone.app.testing import ploneSite
from plone.app.testing import setRoles
from plone.testing import z2
from zope.configuration import xmlconfig

GIF = decodestring(
    'R0lGODlhAQABAPAAAPj8+AAAACH5BAEAAAAALAAAAAABAAEAAAICRAEAOw==')


class LinkIntegrityLayer(z2.Layer):

    defaultBases = (PLONE_FIXTURE, )

    def setUp(self):
        import plone.app.linkintegrity

        xmlconfig.file('configure.zcml', plone.app.linkintegrity,
                       context=self['configurationContext'])

        with ploneSite() as portal:
            setRoles(portal, TEST_USER_ID, ['Manager', ])
            login(portal, TEST_USER_NAME)

            portal.invokeFactory('Document', id='doc1', title='Test Page 1')
            portal.invokeFactory('Document', id='doc2', title='Test Page 2')
            portal.invokeFactory('Document', id='doc3', title='Test Page 3')

            for i in range(1, 4):
                portal.invokeFactory(
                    type_name='Image',
                    id='image%d' % i,
                    title='Test Image %d' % i,
                    image=GIF,
                )

            portal.invokeFactory('File',
                                 id='file1', title='Test File 1', file=GIF)
            portal.invokeFactory('Folder', id='folder1', title='Test Folder 1')

            folder = portal['folder1']
            folder.invokeFactory('Document', id='doc3', title='Test Page 3')
            folder.invokeFactory('Document', id='doc4', title='Test Page 4')
            folder.invokeFactory('Document', id='doc5', title='Test Page 5')

PLONE_APP_LINKINTEGRITY_FIXTURE = LinkIntegrityLayer()

class LinkIntegrityATLayer(LinkIntegrityLayer):

    directory = 'at'
    defaultBases = (
        PLONE_APP_CONTENTTYPES_MIGRATION_FIXTURE,
        PLONE_APP_LINKINTEGRITY_FIXTURE,
    )

PLONE_APP_LINKINTEGRITY_AT_FIXTURE = LinkIntegrityATLayer()


class LinkIntegrityDXLayer(LinkIntegrityLayer):

    directory = 'dx'
    defaultBases = (
        PLONE_APP_CONTENTTYPES_FIXTURE,
        PLONE_APP_LINKINTEGRITY_FIXTURE,
    )

    def setUp(self):
        with ploneSite() as portal:
            ttool = getToolByName(portal, 'portal_types')
            ttool.getTypeInfo('Document').behaviors += (
                'plone.app.referenceablebehavior.referenceable.IReferenceable',
            )

            # FIXME: we need uid_catalog and referencer_catalog to keep
            #        plone.app.referencebehavior working. So load Archetypes
            #        profile to install those tools before we continue
            applyProfile(portal, 'Products.Archetypes:Archetypes')

        super(LinkIntegrityDXLayer, self).setUp()


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
