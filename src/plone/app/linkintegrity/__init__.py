import zope.deferredimport

zope.deferredimport.initialize()


jbot_deprecations = {
    "plone.app.linkintegrity.browser.delete_confirmation_info.pt": "plone.app.layout.controlpanels.templates.linkintegrity_delete_confirmation_info.pt",  # noqa: E501
    "plone.app.linkintegrity.browser.update.pt": "plone.app.layout.controlpanels.templates.linkintegrity_update.pt",  # noqa: E501
}
zope.deferredimport.deprecated(
    "Please use from plone.app.layout.controlpanels.linkintegrity import UpdateView",  # noqa: E501
    UpdateView="plone.app.layout:controlpanels.linkintegrity.UpdateView",
)
