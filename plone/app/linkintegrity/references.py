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

from OFS.interfaces import IItem
from Products.Archetypes.exceptions import ReferenceException
from Products.Archetypes.interfaces import IBaseObject
from Products.CMFCore.utils import getToolByName
from ZODB.POSException import ConflictError
from logging import getLogger


def updateReferences(obj, relationship, newrefs):

    # This for sure looks ugly, but is necessary to maintian AT compatibility
    # newrefs are wrapped objects, but getRefreences returns the real objects
    # to generate a difference, we must do the difference with the objects
    # the adapters wrapped. This is what real_newrefs is about
    # next, when adding references, we have to provide the wrapped object
    # again, so we create a mapping, newref_r_a_mapping to get the
    # wrapped object.

    real_newrefs = set()
    newref_r_a_mapping = {}
    for newref in newrefs:
        # Checking for IItem is a hack to check wether this reference
        # is an adapter or a real object. Real Objects from AT are IItem
        if not IItem.providedBy(newref):
            real_newrefs.add(newref.context)
            newref_r_a_mapping[newref.context] = newref
        else:
            real_newrefs.add(newref)

    existing = set(obj.getReferences(relationship=relationship))

    for ref in real_newrefs.difference(existing):   # add new references and...
        try:
            obj.addReference(newref_r_a_mapping.get(ref, ref), 
                             relationship=relationship)
        except (ReferenceException, AttributeError):
            pass
    for ref in existing.difference(real_newrefs):   # removed leftovers
        try:
            obj.deleteReference(newref_r_a_mapping.get(ref, ref),
                                relationship=relationship)
        except ReferenceException:
            removeDanglingReference(obj, relationship)


def removeDanglingReference(obj, relationship):
    # try to get rid of the dangling reference, but let's not
    # have this attempt to clean up break things otherwise...
    # iow, the `try..except` is there, because internal methods
    # of the reference catalog are being used directly here.  any
    # changes regarding these shouldn't break things over here,
    # though...
    try:
        if not IBaseObject.providedBy(obj) and hasattr(obj, 'context'):
            refcat = getToolByName(obj.context, 'reference_catalog')
        else:
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
