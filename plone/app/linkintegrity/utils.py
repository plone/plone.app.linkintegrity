# -*- coding: utf-8 -*-
from plone.app.linkintegrity.handlers import referencedRelationship
from zc.relation.interfaces import ICatalog
from zope.component import getUtility
from zope.intid.interfaces import IIntIds


def getIncomingLinks(obj):
    """Return a generator of incoming relations created using
    plone.app.linkintegrity (Links in Richtext-Fields).
    """
    catalog = getUtility(ICatalog)
    intids = getUtility(IIntIds)
    return catalog.findRelations({
        'to_id': intids.getId(obj),
        'from_attribute': referencedRelationship})


def hasIncomingLinks(obj):
    """Test if an object is linked to by other objects using
    plone.app.linkintegrity (Links in Richtext-Fields).

    Way to give bool without loading generator into list
    """
    for i in getIncomingLinks(obj):
        return True
    return False


def getOutgoingLinks(obj):
    """Return a generator of outgoing relations created using
    plone.app.linkintegrity (Links in Richtext-Fields).
    """
    catalog = getUtility(ICatalog)
    intids = getUtility(IIntIds)
    return catalog.findRelations({
        'from_id': intids.getId(obj),
        'from_attribute': referencedRelationship})


def hasOutgoingLinks(obj):
    """Test if an object links to other objects using plone.app.linkintegrity
    (Links in Richtext-Fields).
    """
    for i in getOutgoingLinks(obj):
        return True
    return False
