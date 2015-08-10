# -*- coding: utf-8 -*-
from Products.CMFPlone.interfaces import IEditingSchema
from plone.app.linkintegrity.handlers import referencedRelationship
from plone.registry.interfaces import IRegistry
from zc.relation.interfaces import ICatalog
from zope.component import getUtility
from zope.intid.interfaces import IIntIds


def getIncomingLinks(obj=None, intid=None):
    """Return a generator of incoming relations created using
    plone.app.linkintegrity (Links in Richtext-Fields).
    """
    catalog = getUtility(ICatalog)
    if intid is not None:
        return catalog.findRelations({
            'to_id': intid,
            'from_attribute': referencedRelationship})
    else:
        intids = getUtility(IIntIds)
        return catalog.findRelations({
            'to_id': intids.getId(obj),
            'from_attribute': referencedRelationship})


def hasIncomingLinks(obj=None, intid=None):
    """Test if an object is linked to by other objects using
    plone.app.linkintegrity (Links in Richtext-Fields).

    Way to give bool without loading generator into list
    """
    for i in getIncomingLinks(obj=obj, intid=intid):
        return True
    return False


def getOutgoingLinks(obj=None, intid=None):
    """Return a generator of outgoing relations created using
    plone.app.linkintegrity (Links in Richtext-Fields).
    """
    catalog = getUtility(ICatalog)
    if intid is not None:
        return catalog.findRelations({
            'from_id': intid,
            'from_attribute': referencedRelationship})
    else:
        intids = getUtility(IIntIds)
        return catalog.findRelations({
            'from_id': intids.getId(obj),
            'from_attribute': referencedRelationship})


def hasOutgoingLinks(obj=None, intid=None):
    """Test if an object links to other objects using plone.app.linkintegrity
    (Links in Richtext-Fields).
    """
    for i in getOutgoingLinks(obj=obj, intid=intid):
        return True
    return False


def linkintegrity_enabled():
    reg = getUtility(IRegistry)
    editing_settings = reg.forInterface(IEditingSchema, prefix='plone')
    return editing_settings.enable_link_integrity_checks
