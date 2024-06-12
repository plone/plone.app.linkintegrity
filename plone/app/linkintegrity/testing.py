from base64 import decodebytes
from plone.app.testing import layers
from plone.app.testing import login
from plone.app.testing import PLONE_FIXTURE
from plone.app.testing import PloneSandboxLayer
from plone.app.testing import setRoles
from plone.app.testing import TEST_USER_ID
from plone.app.testing import TEST_USER_NAME
from plone.app.testing import TEST_USER_PASSWORD
from plone.namedfile.file import NamedImage
from Products.CMFCore.utils import getToolByName
from zope.configuration import xmlconfig

import io


B64_DATA = b"R0lGODlhAQABAIAAAAUEBAAAACwAAAAAAQABAAACAkQBADs="
GIF = io.BytesIO(decodebytes(B64_DATA))
GIF.filename = "sample.gif"
GIF.contentType = "image/gif"
GIF._width = 1
GIF._height = 1


def create(container, type_name, **kwargs):
    """A easy helper method to create some content since we do not have
    plone.api in core.
    """
    new_id = container.invokeFactory(type_name, **kwargs)
    content = container[new_id]
    return content


class LinkIntegrityLayer(PloneSandboxLayer):
    """Base Layer for Dexterity testing."""

    defaultBases = (PLONE_FIXTURE,)

    def setUpZope(self, app, configurationContext):
        import plone.app.linkintegrity

        xmlconfig.file(
            "configure.zcml", plone.app.linkintegrity, context=configurationContext
        )

    def setUpPloneSite(self, portal):
        setRoles(
            portal,
            TEST_USER_ID,
            [
                "Manager",
            ],
        )
        login(portal, TEST_USER_NAME)

        # Create sample documents
        type_data = dict(type_name="Document")
        for i in range(1, 4):
            type_data["id"] = f"doc{i:d}"
            type_data["title"] = f"Test Page {i:d}"
            create(portal, **type_data)

        create(portal, "File", id="file1", title="File 1", file=GIF)
        create(portal, "Folder", id="folder1", title="Folder 1")
        subfolder = portal["folder1"]
        create(subfolder, "Document", id="doc4", title="Test Page 4")

        # setup members
        pm = getToolByName(portal, "portal_membership")
        pm.addMember("editor", TEST_USER_PASSWORD, ["Editor"], [])
        pm.addMember("member", TEST_USER_PASSWORD, ["Member"], [])
        pm.addMember("authenticated", TEST_USER_PASSWORD, [], [])

        # Create an object that does not provide the behavior to live along
        create(portal, "News Item", id="news1", title="News 1")

        # create a NamedImage
        portal.invokeFactory("Image", "image1")
        portal["image1"].image = NamedImage(GIF, "image/gif", "sample.gif")


PLONE_APP_LINKINTEGRITY_FIXTURE = LinkIntegrityLayer()

PLONE_APP_LINKINTEGRITY_INTEGRATION_TESTING = layers.IntegrationTesting(
    bases=(PLONE_APP_LINKINTEGRITY_FIXTURE,), name="plone.app.linkintegrity:Integration"
)

PLONE_APP_LINKINTEGRITY_FUNCTIONAL_TESTING = layers.FunctionalTesting(
    bases=(PLONE_APP_LINKINTEGRITY_FIXTURE,), name="plone.app.linkintegrity:Functional"
)
