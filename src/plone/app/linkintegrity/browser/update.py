import zope.deferredimport

zope.deferredimport.initialize()
zope.deferredimport.deprecated(
    "Please use from plone.app.layout.controlpanels.linkintegrity import UpdateView",  # noqa: E501
    UpdateView="plone.app.layout:controlpanels.linkintegrity.UpdateView",
)
