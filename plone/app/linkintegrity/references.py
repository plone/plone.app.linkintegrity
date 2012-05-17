# helpers related to reference handling
#
# the following functions can prove helpful outside of `p.a.linkintegrity`,
# but they should really be integrated into `Archetypes` before anybody
# starts using them.  so for now they are provided as a convenience for
# the `plone.app.referenceintegrity` package, but other than that please
# bear in mind the gently reminder that...
#
#	NOBODY ELSE SHOULD IMPORT FROM HERE!!!
#
# you have been warned! :)

from logging import getLogger
from Products.CMFCore.utils import getToolByName
from Products.Archetypes.exceptions import ReferenceException
from ZODB.POSException import ConflictError

try:
    # Imports related to the dexterity support
    from Acquisition import aq_inner
    from z3c.relationfield import RelationValue
    from zc.relation.interfaces import ICatalog
    from zope.component import getUtility
    from zope.intid.interfaces import IIntIds
    HAS_DEXTERITY = True
except:
    HAS_DEXTERITY = False


def updateReferences(obj, relationship, newrefs):
    existing = set(obj.getReferences(relationship=relationship))
    for ref in newrefs.difference(existing):   # add new references and...
        try:
            obj.addReference(ref, relationship=relationship)
        except ReferenceException:
            pass
    for ref in existing.difference(newrefs):   # removed leftovers
        try:
            obj.deleteReference(ref, relationship=relationship)
        except ReferenceException:
            removeDanglingReference(obj, relationship)


def updateDexterityReferences(obj, relationship, newrefs):
    # We use the relation catalog
    catalog = getUtility(ICatalog)
    intids = getUtility(IIntIds)

    # When a relatable dexterity gets modified, an event gets fired in
    # z3c.relationfield.event.updateRelations
    # There, all relations are removed before updating, so if we get here
    # when editing some content, the following line will return empty.
    # However, we leave it, just in case
    relations = catalog.findRelations({'from_id':intids.getId(aq_inner(obj)),
                                       'from_attribute': 'linkintegrity',})

    existing = set([i.to_object for i in relations])

    for ref in newrefs.difference(existing):   # add new references and...
        to_id = intids.register(ref)
        value = RelationValue(to_id)
        # Taken from z3c.relationfield.event._setRelation
        # make sure relation has a __parent__ so we can make an intid for it
        value.__parent__ = obj
        # also set from_object to parent object
        value.from_object = obj
        # and the attribute to the attribute name
        value.from_attribute = 'linkintegrity'
        # now we can create an intid for the relation
        id = intids.register(value)
        # and index the relation with the catalog
        catalog.index_doc(id, value)

    # Same comment as before, when editing a dexterity type, following lines
    # shouldn't do anything, since all relations are removed before
    for ref in existing.difference(newrefs):   # removed leftovers
        for i in relations:
            if i.to_object is ref:
                id = intids.getId(i)
                catalog.unindex_doc(id)


def removeDanglingReference(obj, relationship):
    # try to get rid of the dangling reference, but let's not
    # have this attempt to clean up break things otherwise...
    # iow, the `try..except` is there, because internal methods
    # of the reference catalog are being used directly here.  any
    # changes regarding these shouldn't break things over here,
    # though...
    try:
        refcat = getToolByName(obj, 'reference_catalog')
        uid, dummy = refcat._uidFor(obj)
        brains = refcat._queryFor(uid, None, relationship=relationship)
        objs = refcat._resolveBrains(brains)
        for obj in objs:
            refcat._deleteReference(obj)
    except ConflictError:
        raise
    except:
        getLogger(__name__).warning('dangling "linkintegrity" '
            'reference to %r could not be removed.', obj)
