# -*- coding: utf-8 -*-
from plone.registry.interfaces import IRegistry
from Products.CMFPlone.interfaces import IEditingSchema
from zc.relation.interfaces import ICatalog
from zope.component import getUtility
from zope.intid.interfaces import IIntIds
from zope.keyreference.interfaces import NotYet

referencedRelationship = 'isReferencing'


def getIncomingLinks(
    obj=None,
    intid=None,
    from_attribute=referencedRelationship
):
    """Return a generator of incoming relations created using
    plone.app.linkintegrity (Links in Richtext-Fields).
    """
    catalog = getUtility(ICatalog)
    intid = intid if intid is not None else getUtility(IIntIds).getId(obj)
    query = {'to_id': intid}
    if from_attribute:
        query['from_attribute'] = from_attribute
    return catalog.findRelations(query)


def hasIncomingLinks(obj=None, intid=None):
    """Test if an object is linked to by other objects using
    plone.app.linkintegrity (Links in Richtext-Fields).

    Way to give bool without loading generator into list.
    """
    for it in getIncomingLinks(obj=obj, intid=intid):
        return True
    return False


def getOutgoingLinks(
    obj=None,
    intid=None,
    from_attribute=referencedRelationship
):
    """Return a generator of outgoing relations created using
    plone.app.linkintegrity (Links in Richtext-Fields).
    """
    catalog = getUtility(ICatalog)
    intid = intid if intid is not None else getUtility(IIntIds).getId(obj)
    query = {'from_id': intid}
    if from_attribute:
        query['from_attribute'] = from_attribute
    return catalog.findRelations(query)


def hasOutgoingLinks(obj=None, intid=None):
    """Test if an object links to other objects using plone.app.linkintegrity
    (Links in Richtext-Fields).
    """
    for it in getOutgoingLinks(obj=obj, intid=intid):
        return True
    return False


def linkintegrity_enabled():
    reg = getUtility(IRegistry)
    editing_settings = reg.forInterface(IEditingSchema, prefix='plone')
    return editing_settings.enable_link_integrity_checks


def ensure_intid(obj, intids=None):
    if intids is None:
        intids = getUtility(IIntIds)
    try:
        obj_id = intids.getId(obj)
    except KeyError:
        # In some cases a object is not yet registered by the intid catalog
        try:
            obj_id = intids.register(obj)
        except NotYet:
            # if we get a NotYet error, the object is not
            # attached yet and we will need to get links
            # at a later time when the object has an intid
            return
    return obj_id
